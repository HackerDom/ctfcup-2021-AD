using System.ComponentModel.DataAnnotations;

namespace CtfLand.Service.Models
{
    public class AddAttractionRequestModel
    {
        [Required]
        [MaxLength(100, ErrorMessage = "Максимальная длина названия - 100 символов")]
        public string Name { get; set; }

        [Required]
        public string Description { get; set; }

        [Required]
        [Range(1, int.MaxValue, ErrorMessage = "Стоимость аттракциона должна быть положительным числом")]
        public int Cost { get; set; }
        
        [Required]
        [MaxLength(50, ErrorMessage = "Максимальная длина ключа - 50 символов")]
        public string TicketKey { get; set; }
    }
}