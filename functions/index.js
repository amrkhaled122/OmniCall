/**
 * OmniCall Cloud Functions - Secure API for Desktop App
 * Keeps service account credentials on server, not in desktop app
 */

const functions = require("firebase-functions");
const admin = require("firebase-admin");
const crypto = require("crypto");

// Initialize Firebase Admin SDK
admin.initializeApp();
const db = admin.firestore();

// Helper function to generate random suffix
function generateSuffix(length = 16) {
  const chars = "abcdefghijklmnopqrstuvwxyz0123456789";
  let result = "";
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

// Helper to increment global stats
async function incrementStats(updates) {
  const statsRef = db.collection("stats").doc("global");
  const increment = admin.firestore.FieldValue.increment;
  
  const payload = {};
  if (updates.users) payload.totalUsers = increment(updates.users);
  if (updates.sends) payload.totalSends = increment(updates.sends);
  if (updates.usersToday) payload.usersToday = increment(updates.usersToday);
  
  payload.updatedAt = admin.firestore.FieldValue.serverTimestamp();
  
  await statsRef.set(payload, { merge: true });
}

// API: Create a new user
exports.createUser = functions.https.onCall(async (request, context) => {
  try {
    const data = request.data || request;
    const { displayName } = data;
    
    if (!displayName || typeof displayName !== "string") {
      throw new functions.https.HttpsError("invalid-argument", "displayName is required");
    }
    
    const cleanLabel = displayName.trim();
    const suffix = generateSuffix();
    const base = cleanLabel.toLowerCase().replace(/\s+/g, "-");
    const userId = base ? `${base}-${suffix}` : suffix;
    
    // Create user document
    await db.collection("users").doc(userId).set({
      label: cleanLabel,
      createdAt: admin.firestore.FieldValue.serverTimestamp(),
    });
    
    // Update stats
    await incrementStats({ users: 1, usersToday: 1 });
    
    const pwaUrl = `https://amrkhaled122.github.io/OmniCall/?pair=${userId}`;
    
    return {
      success: true,
      userId: userId,
      pairingUrl: pwaUrl,
    };
  } catch (error) {
    console.error("Error creating user:", error);
    throw new functions.https.HttpsError("internal", error.message);
  }
});

// API: Send notification to user's devices
exports.sendNotification = functions.https.onCall(async (request, context) => {
  try {
    // Extract the actual data (unwrap the double-wrapped structure)
    const data = request.data || request;
    const { userId, message } = data;
    
    if (!userId || typeof userId !== "string") {
      console.error("userId validation failed. userId:", userId, "type:", typeof userId);
      throw new functions.https.HttpsError("invalid-argument", "userId is required");
    }
    
    const notificationMessage = message || "Match found !! Hurry up and accept on your PC !!";
    
    // Get user's FCM tokens
    const tokensSnapshot = await db
      .collection("users")
      .doc(userId)
      .collection("tokens")
      .get();
    
    if (tokensSnapshot.empty) {
      return {
        success: true,
        sent: 0,
        total: 0,
        message: "No devices paired",
      };
    }
    
    const tokens = [];
    tokensSnapshot.forEach((doc) => {
      const tokenData = doc.data();
      if (tokenData.token) {
        tokens.push(tokenData.token);
      }
    });
    
    if (tokens.length === 0) {
      return {
        success: true,
        sent: 0,
        total: 0,
        message: "No valid tokens",
      };
    }
    
    // Send notifications via FCM
    const messages = tokens.map((token) => ({
      token: token,
      notification: {
        title: "OmniCall Alert",
        body: notificationMessage,
      },
      webpush: {
        fcmOptions: {
          link: "https://amrkhaled122.github.io/OmniCall/",
        },
        headers: {
          Urgency: "high",
        },
      },
      android: {
        priority: "high",
      },
    }));
    
    const results = await admin.messaging().sendEach(messages);
    
    const successCount = results.responses.filter((r) => r.success).length;
    const failures = results.responses
      .map((r, idx) => (r.success ? null : tokens[idx]))
      .filter((t) => t !== null);
    
    // Update stats
    if (successCount > 0) {
      // Check if this is from detector (NEW match) or just a test/re-alert
      const userDoc = await db.collection("users").doc(userId).get();
      const userData = userDoc.data() || {};
      const lastDetectorMatchAt = userData.lastDetectorMatchAt;
      
      // Check if message is from detector (contains "Match found")
      const isFromDetector = notificationMessage.includes("Match found");
      
      let isNewMatch = false;
      if (isFromDetector) {
        // This is from the detector - check 60-second cooldown
        isNewMatch = true;
        if (lastDetectorMatchAt) {
          const lastMatchTime = lastDetectorMatchAt.toDate ? lastDetectorMatchAt.toDate().getTime() : 0;
          const now = Date.now();
          const timeDiffSeconds = (now - lastMatchTime) / 1000;
          
          // If less than 60 seconds since last DETECTOR match, it's a re-alert (same game)
          if (timeDiffSeconds < 60) {
            isNewMatch = false;
          }
        }
      }
      
      // ALWAYS increment notificationsSent (raw count: test + detector + re-alerts)
      const updates = {
        notificationsSent: admin.firestore.FieldValue.increment(successCount),
      };
      
      // Only increment matchesFound if it's a NEW detector match (60+ seconds apart)
      if (isNewMatch) {
        updates.matchesFound = admin.firestore.FieldValue.increment(1);
        updates.lastDetectorMatchAt = admin.firestore.FieldValue.serverTimestamp();
        // Update global stats for new matches only
        await incrementStats({ sends: 1 });
      }
      
      await db.collection("users").doc(userId).set(updates, { merge: true });
    }
    
    return {
      success: true,
      sent: successCount,
      total: tokens.length,
      failures: failures,
    };
  } catch (error) {
    console.error("Error sending notification:", error);
    throw new functions.https.HttpsError("internal", error.message);
  }
});

// API: Submit user feedback
exports.submitFeedback = functions.https.onCall(async (request, context) => {
  try {
    const data = request.data || request;
    const { userId, displayName, message } = data;
    
    if (!userId || !displayName || !message) {
      throw new functions.https.HttpsError(
        "invalid-argument",
        "userId, displayName, and message are required"
      );
    }
    
    if (typeof message !== "string" || message.length > 10000) {
      throw new functions.https.HttpsError(
        "invalid-argument",
        "message must be a string under 10000 characters"
      );
    }
    
    await db.collection("feedback").add({
      userId: userId,
      displayName: displayName,
      message: message,
      createdAt: admin.firestore.FieldValue.serverTimestamp(),
    });
    
    return {
      success: true,
      message: "Feedback submitted successfully",
    };
  } catch (error) {
    console.error("Error submitting feedback:", error);
    throw new functions.https.HttpsError("internal", error.message);
  }
});

// API: Get user statistics
exports.getStats = functions.https.onCall(async (request, context) => {
  try {
    const data = request.data || request;
    const { userId } = data;
    
    if (!userId || typeof userId !== "string") {
      throw new functions.https.HttpsError("invalid-argument", "userId is required");
    }
    
    // Get personal stats
    const userDoc = await db.collection("users").doc(userId).get();
    
    if (!userDoc.exists) {
      throw new functions.https.HttpsError("not-found", "User not found");
    }
    
    const userData = userDoc.data();
    const personalMatches = userData.matchesFound || 0;
    const personalNotifs = userData.notificationsSent || 0;
    
    // Get global stats
    const statsDoc = await db.collection("stats").doc("global").get();
    const statsData = statsDoc.exists ? statsDoc.data() : {};
    
    return {
      success: true,
      personal: {
        matchesFound: personalMatches,
        notificationsSent: personalNotifs,
      },
      global: {
        totalUsers: statsData.totalUsers || 0,
        totalSends: statsData.totalSends || 0,
        usersToday: statsData.usersToday || 0,
        updatedAt: statsData.updatedAt ? statsData.updatedAt.toDate().toISOString() : null,
      },
    };
  } catch (error) {
    console.error("Error fetching stats:", error);
    throw new functions.https.HttpsError("internal", error.message);
  }
});
