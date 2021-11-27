using System;
using CtfLand.DataLayer.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;

namespace CtfLand.Service
{
    public class AccessAttribute : Attribute, IActionFilter
    {
        public UserRole Role { get; set; }

        public AccessAttribute(UserRole role)
        {
            Role = role;
        }
        
        public void OnActionExecuting(ActionExecutingContext context)
        {
            if (context.HttpContext.User.GetUserRole() != Role)
                context.Result = new ForbidResult();
        }

        public void OnActionExecuted(ActionExecutedContext context)
        { }
    }
}