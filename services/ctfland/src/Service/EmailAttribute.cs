using System;
using System.ComponentModel.DataAnnotations;
using System.Net.Mail;
using System.Text.RegularExpressions;

namespace CtfLand.Service
{
    public class EmailAttribute : ValidationAttribute
    {
        protected override ValidationResult IsValid(object value, ValidationContext validationContext)
        {
            if (value is not string email)
                return new ValidationResult("Value is not a string");
            
            if (!Regex.IsMatch(email, @"[a-zA-Z0-9()""]+@[a-z][a-zA-Z\.()""]+"))
                return new ValidationResult("Invalid email");

            try
            {
                var _ = new MailAddress(email);
                return ValidationResult.Success;
            }
            catch (FormatException)
            {
                return new ValidationResult("Invalid email");
            }
        }
    }
}