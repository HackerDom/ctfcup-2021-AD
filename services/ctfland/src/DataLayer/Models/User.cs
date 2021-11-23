using System;
using System.ComponentModel.DataAnnotations;

namespace CtfLand.DataLayer.Models
{
    public class User
    {
        [Key]
        public Guid Id { get; set; }

        [Required]
        [MaxLength(50)]
        public string Login { get; set; }

        [Required]
        public string Document { get; set; }

        [Required]
        public UserRole Role { get; set; }

        [Required]
        public DateTime RegisteredAt { get; set; }

        [Required]
        public string PasswordHash { get; set; }

        [Required]
        public byte[] Salt { get; set; }
    }
}