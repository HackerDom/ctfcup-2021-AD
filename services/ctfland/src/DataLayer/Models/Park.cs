using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using JetBrains.Annotations;

namespace CtfLand.DataLayer.Models
{
    [PublicAPI]
    public record Park
    {
        [Key]
        public Guid Id { get; set; }

        [Required]
        public string Name { get; set; }

        [Required]
        public string Contact { get; set; }

        [Required]
        public int MaxVisitorsCount { get; set; }

        [Required]
        public string Description { get; set; }

        [Required]
        public string Template { get; set; }

        [Required]
        public DateTime CreatedAt { get; set; }
        
        [Required]
        public bool IsPublic { get; set; }

        [Required]
        public virtual User Owner { get; set; }

        public virtual ICollection<Attraction> Attractions { get; set; }
    }
}