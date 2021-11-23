using System;
using System.ComponentModel.DataAnnotations;

namespace CtfLand.DataLayer.Models
{
    public class Attraction
    {
        [Key]
        public Guid Id { get; set; }

        [Required]
        public string Name { get; set; }

        [Required]
        public string Description { get; set; }

        [Required]
        public int Cost { get; set; }
    }
}