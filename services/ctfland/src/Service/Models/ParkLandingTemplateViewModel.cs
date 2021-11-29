using System;
using System.Collections.Generic;
using CtfLand.DataLayer.Models;

namespace CtfLand.Service.Models
{
    public class ParkLandingTemplateViewModel
    {
        public Guid UserId { get; set; }
        
        public ICollection<Attraction> Attractions { get; set; }
    }
}