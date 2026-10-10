using System;
using System.Threading.Tasks;
using Firebase.Database;
using Firebase.Database.Query;

namespace NeX_Launcher.State
{
    public static class FirebaseStateManager
    {
        // Replace with actual Firebase Realtime Database URL
        private const string FirebaseUrl = "https://your-project-id.firebaseio.com/";
        private static FirebaseClient _firebaseClient;

        public static void Initialize(Action<string> onModeChanged)
        {
            try
            {
                _firebaseClient = new FirebaseClient(FirebaseUrl);

                _firebaseClient
                    .Child("devices")
                    .Child("laptop_01")
                    .Child("active_mode")
                    .AsObservable<string>()
                    .Subscribe(modeEvent =>
                    {
                        if (modeEvent.Object != null)
                        {
                            string activeMode = modeEvent.Object;
                            onModeChanged?.Invoke(activeMode);
                        }
                    });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Firebase Connection Error: {ex.Message}");
            }
        }

        public static async Task UpdateLastPingAsync(string isoTimestamp)
        {
            if (_firebaseClient == null) return;
            
            try
            {
                await _firebaseClient
                    .Child("devices")
                    .Child("laptop_01")
                    .Child("last_ping")
                    .PutAsync($"\"{isoTimestamp}\"");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Firebase Ping Error: {ex.Message}");
            }
        }
    }
}
