using System.ComponentModel.DataAnnotations;

namespace CtfLand.Service.Models
{
    public class AddAttractionRequestModel
    {
        [Required]
        public string Name { get; set; }

        [Required]
        public string Description { get; set; }

        [Required]
        public int Cost { get; set; }
    }
}