using JetBrains.Annotations;

namespace CtfLand.DataLayer.Models
{
    [PublicAPI]
    public enum UserRole
    {
        Visitor = 0,
        Moderator = 1,
    }
}