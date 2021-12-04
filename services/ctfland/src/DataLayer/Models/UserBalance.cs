using System;
using System.ComponentModel.DataAnnotations;
using JetBrains.Annotations;

namespace CtfLand.DataLayer.Models
{
    [PublicAPI]
    public record UserBalance
    {
        [Key]
        public Guid UserId { get; set; }
        
        [Required]
        public int Balance { get; set; }
    }
}