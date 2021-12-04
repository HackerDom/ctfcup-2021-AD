using System;
using System.ComponentModel.DataAnnotations;
using JetBrains.Annotations;

namespace CtfLand.DataLayer.Models
{
    [PublicAPI]
    public record UserPurchase
    {
        [Key]
        public Guid Id { get; set; }
        
        public Guid UserId { get; set; }
        
        public Guid ParkId { get; set; }
        
        public string Name { get; set; }
    }
}