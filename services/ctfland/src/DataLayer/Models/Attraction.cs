using System;
using System.ComponentModel.DataAnnotations;
using JetBrains.Annotations;

namespace CtfLand.DataLayer.Models
{
    [PublicAPI]
    public record Attraction
    {
        [Key]
        public Guid Id { get; set; }

        [Required]
        public string Name { get; set; }

        [Required]
        public string Description { get; set; }

        [Required]
        public int Cost { get; set; }
        
        [Required]
        public string TicketKey { get; set; }
    }
}