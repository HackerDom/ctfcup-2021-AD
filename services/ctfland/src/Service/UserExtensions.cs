using System;
using System.Linq;
using System.Security.Claims;

namespace CtfLand.Service
{
    public static class UserExtensions
    {
        public static Guid GetUserId(this ClaimsPrincipal claimsPrincipal)
        {
            return Guid.Parse(claimsPrincipal.Claims.First(claim => claim.Type == ClaimTypes.Sid).Value);
        }
    }
}