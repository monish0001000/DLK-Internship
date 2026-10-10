using System;
using System.Security.Cryptography.X509Certificates;

namespace NeX_Launcher.Deployment
{
    public static class SignatureValidator
    {
        public static bool VerifyPublisher(string filePath)
        {
            try
            {
                X509Certificate signer = X509Certificate.CreateFromSignedFile(filePath);
                X509Certificate2 cert = new X509Certificate2(signer);
                
                // For this implementation, we will verify the certificate chain.
                // In a true enterprise MDM scenario, you would also verify the Subject CN
                // e.g. cert.Subject.Contains("O=Microsoft Corporation")
                
                X509Chain chain = new X509Chain();
                chain.ChainPolicy.RevocationMode = X509RevocationMode.Online;
                chain.ChainPolicy.RevocationFlag = X509RevocationFlag.ExcludeRoot;
                
                bool isValid = chain.Build(cert);
                
                if (isValid)
                {
                    FileLogger.Log($"[SignatureValidator] Valid signature found for {filePath} from {cert.Subject}");
                    return true;
                }
                else
                {
                    FileLogger.Log($"[SignatureValidator] Invalid certificate chain for {filePath}");
                    return false;
                }
            }
            catch (Exception ex)
            {
                FileLogger.Log($"[SignatureValidator] Signature check failed for {filePath}: {ex.Message}");
                return false;
            }
        }
    }
}
