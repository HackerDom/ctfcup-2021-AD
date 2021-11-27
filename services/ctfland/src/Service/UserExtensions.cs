using System;
using System.Linq;
using System.Security.Claims;
using CtfLand.DataLayer.Models;

namespace CtfLand.Service
{
    public static class UserExtensions
    {
        public static Guid GetUserId(this ClaimsPrincipal claimsPrincipal)
        {
            return Guid.Parse(claimsPrincipal.Claims.First(claim => claim.Type == ClaimTypes.Sid).Value);
        }

        public static bool IsVisitor(this User user)
        {
            return user.Role == UserRole.Visitor;
        }
    }
}