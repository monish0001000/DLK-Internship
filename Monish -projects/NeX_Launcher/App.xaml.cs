using System;
using System.Diagnostics;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Threading;
using NeX_Launcher.Deployment;

namespace NeX_Launcher
{
    public partial class App : System.Windows.Application
    {
        public App()
        {
            this.DispatcherUnhandledException += App_DispatcherUnhandledException;
            AppDomain.CurrentDomain.UnhandledException += CurrentDomain_UnhandledException;
            TaskScheduler.UnobservedTaskException += TaskScheduler_UnobservedTaskException;
            this.Exit += App_Exit;
            this.SessionEnding += App_SessionEnding;
        }

        private void App_Exit(object sender, ExitEventArgs e)
        {
            FileLogger.Log($"[App.Exit] Application exiting with code {e.ApplicationExitCode}. Trace:\n{Environment.StackTrace}");
        }

        private void App_SessionEnding(object sender, SessionEndingCancelEventArgs e)
        {
            FileLogger.Log($"[App.SessionEnding] Reason: {e.ReasonSessionEnding}");
        }

        protected override void OnStartup(StartupEventArgs e)
        {
            FileLogger.Log("[App.OnStartup] Application startup initiated.");
            base.OnStartup(e);
        }

        private void App_DispatcherUnhandledException(object sender, DispatcherUnhandledExceptionEventArgs e)
        {
            FileLogger.LogError(e.Exception, "UI Dispatcher Unhandled Exception");
            e.Handled = true;
        }

        private void CurrentDomain_UnhandledException(object sender, UnhandledExceptionEventArgs e)
        {
            if (e.ExceptionObject as Exception is Exception ex)
            {
                FileLogger.LogError(ex, $"Background Domain Exception (IsTerminating: {e.IsTerminating})");
            }
            else
            {
                FileLogger.Log($"[Fatal Error] Unknown Background Domain Exception. IsTerminating: {e.IsTerminating}");
            }
        }

        private void TaskScheduler_UnobservedTaskException(object sender, UnobservedTaskExceptionEventArgs e)
        {
            FileLogger.LogError(e.Exception, "Unobserved Task Exception");
            e.SetObserved();
        }
    }
}
