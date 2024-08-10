using System;
using System.ComponentModel.DataAnnotations;

namespace FraudSquad.Models
{
    public class Report
    {
        public Report()
        {
            Name = string.Empty;
            ID = string.Empty;
            Sex = string.Empty;
            Email = string.Empty;
            Phone = string.Empty;
            Race = string.Empty;
            Nationality = string.Empty;
            Occupation = string.Empty;
            PostalCode = string.Empty;
            BlockHouseNumber = string.Empty;
            Street = string.Empty;
            Building = string.Empty;
            FloorUnit = string.Empty;
            ScamDescription = string.Empty;
            URL = string.Empty;
        }

        [Required]
        public string Name { get; set; }
        
        [Required]
        public string ID { get; set; }
        
        [Required]
        public string Sex { get; set; }
        
        [Required]
        public DateTime DOB { get; set; }
        
        [Required]
        [EmailAddress]
        public string Email { get; set; }
        
        [Required]
        [Phone]
        public string Phone { get; set; }
        
        [Required]
        public string Race { get; set; }
        
        [Required]
        public string Nationality { get; set; }
        
        [Required]
        public string Occupation { get; set; }
        
        [Required]
        public string PostalCode { get; set; }
        
        [Required]
        public string BlockHouseNumber { get; set; }
        
        [Required]
        public string Street { get; set; }

        [Required]
        public string Building { get; set; }
        
        [Required]
        public string FloorUnit { get; set; }
        
        [Required]
        public string ScamDescription { get; set; }
        
        public string URL { get; set; }
    }
}
