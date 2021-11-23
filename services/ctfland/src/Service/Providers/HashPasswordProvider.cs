using System;
using System.Security.Cryptography;
using Microsoft.AspNetCore.Cryptography.KeyDerivation;

namespace CtfLand.Service.Providers
{
    public class HashPasswordProvider
    {
        public (string hash, byte[] salt) GetPasswordHash(string password)
        {
            var salt = GetSalt();
            return (GetPasswordHash(password, salt), salt);
        }

        public bool IsPasswordCorrect(string password, byte[] salt, string hash)
        {
            return GetPasswordHash(password, salt) == hash;
        }

        private static byte[] GetSalt()
        {
            var salt = new byte[128 / 8];
            using var rng = RandomNumberGenerator.Create();
            rng.GetBytes(salt);

            return salt;
        }

        private static string GetPasswordHash(string password, byte[] salt)
        {
            var keyDerivation = KeyDerivation.Pbkdf2(
                password,
                salt,
                KeyDerivationPrf.HMACSHA1,
                10000,
                256 / 8);
            return Convert.ToBase64String(keyDerivation);
        }
    }
}