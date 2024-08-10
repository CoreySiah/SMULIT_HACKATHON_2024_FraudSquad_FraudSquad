using System.Diagnostics;
using Microsoft.AspNetCore.Mvc;
using FraudSquad.Models;
using System.Globalization;
using System.IO;
using CsvHelper;
using Microsoft.Extensions.Logging;
using OfficeOpenXml;

namespace FraudSquad.Controllers
{
    public class HomeController : Controller
    {
        private readonly ILogger<HomeController> _logger;

        public HomeController(ILogger<HomeController> logger)
        {
            _logger = logger;
        }

        public IActionResult Index()
        {
            return View();
        }

        public IActionResult Report()
        {
            return View();
        }

        [HttpPost]
        public IActionResult Report(Report report)
        {
            if (ModelState.IsValid)
            {
                try
                {
                    _logger.LogInformation("Model is valid. Attempting to save report.");
                    SaveReportToCsv(report);
                    _logger.LogInformation("Report saved to CSV successfully.");
                    RunPythonScript();
                }
                catch (Exception ex)
                {
                    _logger.LogError("An error occurred while saving the report: " + ex.Message);
                }
                return RedirectToAction("Index");
            }

            _logger.LogWarning("Model state is invalid.");
            return View(report);
        }

        private void SaveReportToCsv(Report report)
        {
            var path = Path.Combine(Directory.GetCurrentDirectory(), "data", "reports.csv");
            _logger.LogInformation("Saving report to: " + path);

            var appendHeader = !System.IO.File.Exists(path);

            using (var writer = new StreamWriter(path, true))
            using (var csv = new CsvWriter(writer, CultureInfo.InvariantCulture))
            {
                if (appendHeader)
                {
                    csv.WriteHeader<Report>();
                    csv.NextRecord();
                }
                csv.WriteRecord(report);
                csv.NextRecord();
            }
        }
        private void RunPythonScript()
        {
            try
            {
                var start = new ProcessStartInfo
                {
                    FileName = "python",
                    Arguments = "./Blocker/py/test.py",
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                };

                using (var process = Process.Start(start))
                {
                    process.WaitForExit();
                    string result = process.StandardOutput.ReadToEnd();
                    string errors = process.StandardError.ReadToEnd();

                    _logger.LogInformation("Python script output: " + result);

                    if (!string.IsNullOrEmpty(errors))
                    {
                        _logger.LogError("Python script errors: " + errors);
                    }
                }
            }
            catch (Exception ex)
            {
                _logger.LogError("Failed to run Python script: " + ex.Message);
            }
        }

        public IActionResult Appeal()
        {
            return View();
        }

        
        [HttpPost]
        public IActionResult Appeal(Appeal appeal)
        {
            if (ModelState.IsValid)
            {
                try
                {
                    _logger.LogInformation("Model is valid. Attempting to save appeal.");
                    SaveAppealToCsv(appeal);
                    _logger.LogInformation("Appeal saved to CSV successfully.");
                    // RunPythonScript();
                }
                catch (Exception ex)
                {
                    _logger.LogError("An error occurred while saving the appeal: " + ex.Message);
                }
                return RedirectToAction("Index");
            }

            _logger.LogWarning("Model state is invalid.");
            return View(appeal);
        }

        private void SaveAppealToCsv(Appeal appeal)
        {
            var path = Path.Combine(Directory.GetCurrentDirectory(), "data", "appeals.csv");
            _logger.LogInformation("Saving appeal to: " + path);

            var appendHeader = !System.IO.File.Exists(path);

            using (var writer = new StreamWriter(path, true))
            using (var csv = new CsvWriter(writer, CultureInfo.InvariantCulture))
            {
                if (appendHeader)
                {
                    csv.WriteHeader<Report>();
                    csv.NextRecord();
                }
                csv.WriteRecord(appeal);
                csv.NextRecord();
            }
        }

        public IActionResult Sites()
        {
            string filePath = Path.Combine(Directory.GetCurrentDirectory(), "data", "blacklist.csv");
            List<string> bannedSites = new List<string>();

            if (System.IO.File.Exists(filePath))
            {
                using (var reader = new StreamReader(filePath))
                {
                    bool headerSkipped = false;

                    while (!reader.EndOfStream)
                    {
                        var line = reader.ReadLine();

                        // Skip header
                        if (!headerSkipped)
                        {
                            headerSkipped = true;
                            continue;
                        }

                        if (!string.IsNullOrWhiteSpace(line))
                        {
                            bannedSites.Add(line.Trim());
                        }
                    }
                }
            }

            return View(bannedSites);
        }

        [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
        public IActionResult Error()
        {
            return View(new ErrorViewModel { RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier });
        }
    }
}
