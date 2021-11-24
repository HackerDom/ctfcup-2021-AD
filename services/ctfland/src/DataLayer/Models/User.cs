using System;
using System.ComponentModel.DataAnnotations;
using System.Text;

namespace CtfLand.DataLayer.Models
{
    public record User
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
        
        protected virtual bool PrintMembers(StringBuilder stringBuilder)
        {
            // hide password hash and salt fields from printing at logs
            stringBuilder.Append($"Id = {Id}, Login = {Login}, ");
            stringBuilder.Append($"Document = {Document}, Role = {Role}, RegisteredAt = {RegisteredAt}");
            return true;
        }
    }
}