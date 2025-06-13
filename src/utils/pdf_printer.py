"""
PDF Printing Utility for the PisoPrint Vendo system.
Handles PDF printing operations using SumatraPDF.
"""
import os
import subprocess
import sys
import win32print
import winreg
from tkinter import messagebox
from src.config import SUMATRA_PATHS
from src.utils.logger import logger, log_error, log_print_job

class PDFPrinter:
    """Handles PDF printing operations using SumatraPDF"""
    
    def __init__(self, printer_name=None):
        """
        Initialize the PDFPrinter with a specific printer or the system default.
        
        Args:
            printer_name (str, optional): Name of the printer to use. Defaults to system default.
        """
        self.printer_name = printer_name or win32print.GetDefaultPrinter()
        self.sumatra_path = self._find_sumatra_path()
        logger.info(f"PDFPrinter initialized with printer: {self.printer_name}")
        logger.info(f"SumatraPDF path: {self.sumatra_path}")
        
    def _find_sumatra_path(self):
        """
        Find the SumatraPDF executable path from registry or common locations.
        
        Returns:
            str: Path to SumatraPDF executable or None if not found
        """
        # Check registry
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                              r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\SumatraPDF.exe") as key:
                reg_path = winreg.QueryValue(key, None)
                if os.path.exists(reg_path):
                    logger.info(f"Found SumatraPDF in registry: {reg_path}")
                    return reg_path
        except WindowsError:
            logger.debug("SumatraPDF not found in registry")
            pass

        # Check common paths from config
        for path in SUMATRA_PATHS:
            if os.path.exists(path):
                logger.info(f"Found SumatraPDF at: {path}")
                return path
                
        # Search in PATH
        for path in os.environ["PATH"].split(os.pathsep):
            exe_path = os.path.join(path, "SumatraPDF.exe")
            if os.path.exists(exe_path):
                logger.info(f"Found SumatraPDF in PATH: {exe_path}")
                return exe_path
                
        logger.warning("SumatraPDF not found")
        return None

    def _install_sumatra(self):
        """
        Guide user to install SumatraPDF.
        
        Returns:
            bool: False to indicate print operation failed
        """
        msg = ("SumatraPDF is required for printing and needs to be installed.\n\n"
               "Please follow these steps:\n"
               "1. Download SumatraPDF from https://www.sumatrapdfreader.org/download-free-pdf-viewer\n"
               "2. Install it with default settings\n"
               "3. Try printing again")
        messagebox.showinfo("Printer Setup Required", msg)
        logger.warning("Prompted user to install SumatraPDF")
        return False

    def print_pdf(self, pdf_path, copies=1, print_settings=None):
        """
        Print PDF using SumatraPDF with advanced settings.
        
        Args:
            pdf_path (str): Path to the PDF file to print
            copies (int, optional): Number of copies to print. Defaults to 1.
            print_settings (dict, optional): Additional print settings. Defaults to None.
                Possible settings:
                - 'range': Page range (e.g., '1-5,10')
                - 'scale': Scale factor (e.g., 'fit' or '100')
                - 'duplex': Enable duplex printing (bool)
        
        Returns:
            bool: True if print job was sent successfully, False otherwise
        """
        try:
            if not os.path.exists(pdf_path):
                error_msg = f"PDF file not found: {pdf_path}"
                log_error("PDFPrinter", error_msg)
                raise FileNotFoundError(error_msg)

            # Check if SumatraPDF is installed
            if not self.sumatra_path:
                return self._install_sumatra()

            # Build command for SumatraPDF
            settings_str = f"copies={copies}"
            
            # Add additional print settings if provided
            if print_settings:
                if 'range' in print_settings:
                    settings_str += f",print-range={print_settings['range']}"
                if 'scale' in print_settings:
                    settings_str += f",scale={print_settings['scale']}"
                if print_settings.get('duplex', False):
                    settings_str += ",duplex"
            
            cmd = [
                self.sumatra_path,
                "-print-to", self.printer_name,
                "-print-settings", settings_str,
                pdf_path
            ]
            
            logger.info(f"Printing PDF: {pdf_path}")
            logger.info(f"Print command: {' '.join(cmd)}")
            
            # Execute print command
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if process.returncode == 0:
                log_print_job(os.path.basename(pdf_path), copies, 0)  # 0 will be updated with actual page count
                logger.info("Print command sent successfully")
                return True
            else:
                error_msg = f"Print command failed with return code {process.returncode}: {process.stderr}"
                log_error("PDFPrinter", error_msg)
                raise Exception(error_msg)

        except Exception as e:
            error_msg = f"Printing error: {str(e)}"
            log_error("PDFPrinter", error_msg)
            messagebox.showerror("Printing Error", error_msg)
            return False

    def check_printer_status(self):
        """
        Check if printer is ready and get its detailed status.
        
        Returns:
            dict: Printer status information
        """
        try:
            # First check if SumatraPDF is installed
            if not self.sumatra_path:
                logger.warning("SumatraPDF not installed, cannot check printer status")
                return {"status": "error", "message": "SumatraPDF not installed"}
                
            printer_handle = win32print.OpenPrinter(self.printer_name)
            try:
                printer_info = win32print.GetPrinter(printer_handle, 2)
                status_code = printer_info['Status']
                
                # Interpret status code
                status = {
                    "code": status_code,
                    "ready": status_code == 0,
                    "details": {}
                }
                
                # Parse status bits
                if status_code & 0x00000001:
                    status["details"]["paused"] = True
                if status_code & 0x00000002:
                    status["details"]["error"] = True
                if status_code & 0x00000004:
                    status["details"]["pending_deletion"] = True
                if status_code & 0x00000008:
                    status["details"]["paper_jam"] = True
                if status_code & 0x00000010:
                    status["details"]["paper_out"] = True
                if status_code & 0x00000020:
                    status["details"]["manual_feed"] = True
                if status_code & 0x00000040:
                    status["details"]["paper_problem"] = True
                if status_code & 0x00000080:
                    status["details"]["offline"] = True
                
                logger.info(f"Printer status: {status}")
                return status
                
            finally:
                win32print.ClosePrinter(printer_handle)
                
        except Exception as e:
            error_msg = f"Error checking printer status: {e}"
            log_error("PDFPrinter", error_msg)
            return {"status": "error", "message": str(e)}
            
    def list_available_printers(self):
        """
        List all available printers on the system.
        
        Returns:
            list: List of printer names
        """
        printers = []
        try:
            for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS):
                printers.append(printer[2])
            logger.info(f"Available printers: {printers}")
            return printers
        except Exception as e:
            log_error("PDFPrinter", f"Error listing printers: {e}")
            return []
            
    def set_printer(self, printer_name):
        """
        Set the printer to use for printing.
        
        Args:
            printer_name (str): Name of the printer to use
            
        Returns:
            bool: True if printer was set successfully, False otherwise
        """
        try:
            # Check if printer exists
            printers = self.list_available_printers()
            if printer_name not in printers:
                log_error("PDFPrinter", f"Printer not found: {printer_name}")
                return False
                
            self.printer_name = printer_name
            logger.info(f"Printer set to: {printer_name}")
            return True
        except Exception as e:
            log_error("PDFPrinter", f"Error setting printer: {e}")
            return False