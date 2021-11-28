using System.ComponentModel.DataAnnotations;

namespace CtfLand.Service.Models
{
    public class LoginRequestModel
    {
        [Required(ErrorMessage = "Не указан логин")]
        public string Login { get; set; }

        [Required(ErrorMessage = "Не указан пароль")]
        [DataType(DataType.Password)]
        public string Password { get; set; }
        
        public string ReturnUrl { get; set; }
    }
}