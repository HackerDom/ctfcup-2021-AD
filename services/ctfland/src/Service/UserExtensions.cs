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
        
        public static UserRole GetUserRole(this ClaimsPrincipal claimsPrincipal)
        {
            return Enum.TryParse<UserRole>(
                claimsPrincipal.Claims.First(claim => claim.Type == ClaimTypes.Role).Value,
                out var role)
                ? role
                : UserRole.Moderator;
        }
        
        public static bool IsVisitor(this ClaimsPrincipal claimsPrincipal)
        {
            return claimsPrincipal.GetUserRole() == UserRole.Visitor;
        }

        public static bool IsVisitor(this User user)
        {
            return user.Role == UserRole.Visitor;
        }
    }
}