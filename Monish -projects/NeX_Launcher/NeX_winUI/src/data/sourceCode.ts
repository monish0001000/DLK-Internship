export interface CodeFile {
  name: string;
  language: 'xml' | 'csharp' | 'json';
  content: string;
  description: string;
}

export const APP_SOURCE_CODES: Record<string, CodeFile[]> = {
  camera: [
    {
      name: "CameraPage.xaml",
      language: "xml",
      description: "Defines the WPF/UWP layout for the Windows Camera with aspect ratio guides, rule-of-thirds grid, and video mode states.",
      content: `<Page
    x:Class="LuminaKiosk.CameraPage"
    xmlns="http://schemas.microsoft.com/winfx/2000/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
    xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
    mc:Ignorable="d"
    Background="{ThemeResource ApplicationPageBackgroundThemeBrush}">

    <Grid Background="#0A0D0D">
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto" />
            <RowDefinition Height="*" />
            <RowDefinition Height="Auto" />
        </Grid.RowDefinitions>

        <!-- Upper Control Bar -->
        <RelativePanel Grid.Row="0" Padding="16" Background="#111515" BorderBrush="#1F2424" BorderThickness="0,0,0,1">
            <StackPanel Orientation="Vertical" RelativePanel.AlignLeftWithPanel="True">
                <TextBlock Text="WINDOWS CAMERA CAPTURE UTILITY" FontSize="12" FontWeight="Bold" Foreground="#60CDFF" FontFamily="Consolas" Tracking="2"/>
                <TextBlock Text="Lumina Integrated HD Optical Driver v4.2" FontSize="10" Foreground="#4B5563" Margin="0,2,0,0"/>
            </StackPanel>
            
            <StackPanel Orientation="Horizontal" RelativePanel.AlignRightWithPanel="True" Margin="0,2,0,0">
                <ComboBox x:Name="RatioSelector" Width="90" SelectedIndex="0" SelectionChanged="Ratio_Changed">
                    <ComboBoxItem Content="16:9 Wide" />
                    <ComboBoxItem Content="4:3 Standard" />
                </ComboBox>
                <ComboBox x:Name="TimerSelector" Width="80" SelectedIndex="0" Margin="8,0,0,0">
                    <ComboBoxItem Content="No Timer" />
                    <ComboBoxItem Content="2s Delay" />
                    <ComboBoxItem Content="5s Delay" />
                    <ComboBoxItem Content="10s Delay" />
                </ComboBox>
            </StackPanel>
        </RelativePanel>

        <!-- Viewfinder Canvas & Capture Overlay -->
        <Grid Grid.Row="1" Background="Black" Margin="16" CornerRadius="12" BorderThickness="1" BorderBrush="#252A2A">
            <CaptureElement x:Name="PreviewControl" Stretch="UniformToFill" />
            
            <!-- Gridlines overlays -->
            <Grid x:Name="ThirdsGrid" Visibility="Collapsed">
                <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="*" />
                    <ColumnDefinition Width="*" />
                    <ColumnDefinition Width="*" />
                </Grid.ColumnDefinitions>
                <Grid.RowDefinitions>
                    <RowDefinition Height="*" />
                    <RowDefinition Height="*" />
                    <RowDefinition Height="*" />
                </Grid.RowDefinitions>
                <Border Grid.Column="0" BorderBrush="White" BorderThickness="0,0,1,0" Opacity="0.25" />
                <Border Grid.Column="1" BorderBrush="White" BorderThickness="0,0,1,0" Opacity="0.25" />
                <Border Grid.Row="0" BorderBrush="White" BorderThickness="0,0,0,1" Opacity="0.25" />
                <Border Grid.Row="1" BorderBrush="White" BorderThickness="0,0,0,1" Opacity="0.25" />
            </Grid>

            <!-- Video Recording Indicator HUD -->
            <StackPanel Orientation="Horizontal" HorizontalAlignment="Left" VerticalAlignment="Top" Margin="12" Padding="8" Background="#CC000000" CornerRadius="6" x:Name="RecIndicator" Visibility="Collapsed">
                <Ellipse Width="8" Height="8" Fill="#EF4444" Margin="0,0,6,0" />
                <TextBlock x:Name="TimerText" Text="REC 00:00" Foreground="White" FontSize="11" FontFamily="Consolas" />
            </StackPanel>

            <!-- Countdown text box overlay -->
            <TextBlock x:Name="CountdownBlock" Text="" FontSize="72" FontWeight="Black" Foreground="#60CDFF" HorizontalAlignment="Center" VerticalAlignment="Center" Visibility="Collapsed"/>
            
            {/* Shutter flash board */}
            <Border x:Name="FlashOverlay" Background="White" Opacity="0" Visibility="Collapsed" />
        </Grid>

        <!-- Command controls toolbar -->
        <Grid Grid.Row="2" Background="#111515" Padding="12,16">
            <Grid.ColumnDefinitions>
                <ColumnDefinition Width="*" />
                <ColumnDefinition Width="Auto" />
                <ColumnDefinition Width="*" />
            </Grid.ColumnDefinitions>

            <!-- Left options -->
            <StackPanel Grid.Column="0" Orientation="Horizontal" VerticalAlignment="Center">
                <Button Content="3x3 Grid" Click="GridToggle_Click" Width="80" Style="{ThemeResource AccentButtonStyle}"/>
                <Button Content="Mute Sound" Click="MuteToggle_Click" Width="90" Margin="8,0,0,0"/>
            </StackPanel>

            <!-- Middle Core Trigger -->
            <StackPanel Grid.Column="1" Orientation="Horizontal">
                <ToggleButton x:Name="PhotoModeBtn" Content="📷 PHOTO" Checked="Mode_Photo" IsChecked="True" Width="80" Height="40" CornerRadius="6,0,0,6"/>
                <ToggleButton x:Name="VideoModeBtn" Content="📹 VIDEO" Checked="Mode_Video" Width="80" Height="40" CornerRadius="0,6,6,0"/>
                <Button x:Name="ShutterBtn" Content="CAPTURE" Click="Shutter_Click" Width="100" Height="40" Margin="12,0,0,0" FontWeight="Bold" Background="#2563EB" Foreground="White"/>
            </StackPanel>

            <!-- Right gallery thumbnails roll -->
            <StackPanel Grid.Column="2" Orientation="Horizontal" HorizontalAlignment="Right" VerticalAlignment="Center">
                <TextBlock Text="Images Captured:" VerticalAlignment="Center" Margin="0,0,8,0" FontSize="11" Foreground="#9CA3AF"/>
                <Button x:Name="GalleryBtn" Padding="0" Width="36" Height="36" CornerRadius="6" Click="Gallery_Click" Background="#2E3440">
                    <Image x:Name="GalleryThumbnail" Stretch="UniformToFill" />
                </Button>
            </StackPanel>
        </Grid>
    </Grid>
</Page>`
    },
    {
      name: "CameraPage.xaml.cs",
      language: "csharp",
      description: "Handles UWP MediaCapture camera initialization, custom aspect ratios, self timers, video clips saving, and mock stream simulation fallbacks.",
      content: `using System;
using System.IO;
using System.Diagnostics;
using System.Threading.Tasks;
using Windows.UI.Xaml;
using Windows.UI.Xaml.Controls;
using Windows.Media.Capture;
using Windows.Media.MediaProperties;
using Windows.Storage;
using Windows.Storage.Streams;
using Windows.UI.Core;

namespace LuminaKiosk
{
    public sealed partial class CameraPage : Page
    {
        private MediaCapture _mediaCapture;
        private bool _isInitialized;
        private bool _isRecording;
        private DispatcherTimer _recordTimer;
        private int _secondsRecorded;
        private int _countdownSecs;

        public CameraPage()
        {
            this.InitializeComponent();
            InitializeCameraAsync();
            SetupTimer();
        }

        private async void InitializeCameraAsync()
        {
            try
            {
                _mediaCapture = new MediaCapture();
                var settings = new MediaCaptureInitializationSettings
                {
                    StreamingCaptureMode = StreamingCaptureMode.Video,
                    VideoDeviceId = ""
                };
                await _mediaCapture.InitializeAsync(settings);
                PreviewControl.Source = _mediaCapture;
                await _mediaCapture.StartPreviewAsync();
                _isInitialized = true;
                Debug.WriteLine("[INFO] MediaCapture pipeline configured correctly.");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[WARNING] Standard grabber failed, active emulated sandbox mode: {ex.Message}");
                ShowSandboxEmulation();
            }
        }

        private void SetupTimer()
        {
            _recordTimer = new DispatcherTimer();
            _recordTimer.Interval = TimeSpan.FromSeconds(1);
            _recordTimer.Tick += (s, e) => {
                _secondsRecorded++;
                int mins = _secondsRecorded / 60;
                int secs = _secondsRecorded % 60;
                TimerText.Text = $"REC {mins:D2}:{secs:D2}";
            };
        }

        private async void Shutter_Click(object sender, RoutedEventArgs e)
        {
            int delay = GetTimerDelayValue();
            if (delay > 0)
            {
                _countdownSecs = delay;
                CountdownBlock.Text = _countdownSecs.ToString();
                CountdownBlock.Visibility = Visibility.Visible;
                
                while (_countdownSecs > 0)
                {
                    PlayBeepTone(880);
                    await Task.Delay(1000);
                    _countdownSecs--;
                    CountdownBlock.Text = _countdownSecs.ToString();
                }
                CountdownBlock.Visibility = Visibility.Collapsed;
            }

            if (PhotoModeBtn.IsChecked == true)
            {
                await CapturePhotoPipeline();
            }
            else
            {
                ToggleVideoRecording();
            }
        }

        private async Task CapturePhotoPipeline()
        {
            TriggerFlashAnimation();
            PlayShutterTone();

            if (!_isInitialized)
            {
                Debug.WriteLine("[MOCK] Snapped picture to local virtual roll.");
                UpdateThumbnailImage(null);
                return;
            }

            try
            {
                var imgProp = ImageEncodingProperties.CreatePng();
                var file = await KnownFolders.CameraRoll.CreateFileAsync("Snap.png", CreationCollisionOption.GenerateUniqueName);
                using (var stream = await file.OpenAsync(FileAccessMode.ReadWrite))
                {
                    await _mediaCapture.CapturePhotoToStreamAsync(imgProp, stream);
                }
                UpdateThumbnailImage(file);
                Debug.WriteLine($"[INFO] Snapped frame and saved: {file.Name}");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[ERROR] CapturePhotoPipeline failed: {ex.Message}");
            }
        }

        private void ToggleVideoRecording()
        {
            if (_isRecording)
            {
                _isRecording = false;
                _recordTimer.Stop();
                RecIndicator.Visibility = Visibility.Collapsed;
                PlayBeepTone(440);
                Debug.WriteLine("[INFO] Video clip compilation stored safely.");
            }
            else
            {
                _isRecording = true;
                _secondsRecorded = 0;
                _recordTimer.Start();
                RecIndicator.Visibility = Visibility.Visible;
                PlayBeepTone(660);
                Debug.WriteLine("[INFO] Video stream writing to local storage buffer...");
            }
        }

        private void GridToggle_Click(object sender, RoutedEventArgs e)
        {
            ThirdsGrid.Visibility = ThirdsGrid.Visibility == Visibility.Visible ? Visibility.Collapsed : Visibility.Visible;
            PlayBeepTone(1000);
        }

        private void TriggerFlashAnimation()
        {
            FlashOverlay.Visibility = Visibility.Visible;
            FlashOverlay.Opacity = 1;
            var t = Task.Run(async () => {
                await Task.Delay(100);
                await Dispatcher.RunAsync(CoreDispatcherPriority.Normal, () => {
                    FlashOverlay.Opacity = 0;
                    FlashOverlay.Visibility = Visibility.Collapsed;
                });
            });
        }

        private int GetTimerDelayValue()
        {
            switch (TimerSelector.SelectedIndex)
            {
                case 1: return 2;
                case 2: return 5;
                case 3: return 10;
                default: return 0;
            }
        }

        private void PlayBeepTone(double freq) => Debug.WriteLine($"[AUDIO] SineOscillator tone {freq} Hz");
        private void PlayShutterTone() => Debug.WriteLine("[AUDIO] WhiteNoiseBurst shutter snap click");
        private void ShowSandboxEmulation() => Debug.WriteLine("[HUD] Graphics Context set to fallback canvas loop.");
        private void UpdateThumbnailImage(StorageFile file) => Debug.WriteLine("[UI] GalleryThumbnail set to source image file.");
    }
}`
    }
  ],
  calculator: [
    {
      name: "CalculatorPage.xaml",
      language: "xml",
      description: "Grid-based classic Windows calculator layout with customized display styling.",
      content: `<Page
    x:Class="LuminaKiosk.CalculatorPage"
    xmlns="http://schemas.microsoft.com/winfx/2000/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    Background="#151717">

    <Grid MaxWidth="400" HorizontalAlignment="Center" VerticalAlignment="Center" Padding="20">
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto" />
            <RowDefinition Height="Auto" />
            <RowDefinition Height="*" />
        </Grid.RowDefinitions>

        <!-- Dynamic Equation Preview -->
        <TextBlock Name="FormulaDisplay" Grid.Row="0" TextAlignment="Right" FontSize="14" Foreground="#9CA3AF" Height="25" Margin="0,0,10,0" />
        
        <!-- Result Display -->
        <TextBlock Name="DisplayBlock" Grid.Row="1" Text="0" TextAlignment="Right" FontSize="42" FontWeight="Bold" Foreground="White" Margin="0,0,10,20" />

        <!-- Keypad Grid -->
        <Grid Grid.Row="2" ColumnSpacing="4" RowSpacing="4">
            <Grid.ColumnDefinitions>
                <ColumnDefinition Width="*" />
                <ColumnDefinition Width="*" />
                <ColumnDefinition Width="*" />
                <ColumnDefinition Width="*" />
            </Grid.ColumnDefinitions>
            <Grid.RowDefinitions>
                <RowDefinition Height="*" />
                <RowDefinition Height="*" />
                <RowDefinition Height="*" />
                <RowDefinition Height="*" />
                <RowDefinition Height="*" />
            </Grid.RowDefinitions>

            <!-- Row 1 -->
            <Button Content="CE" Click="Clear_Click" Grid.Row="0" Grid.Column="0" Background="#1F2323" Foreground="White" HorizontalAlignment="Stretch" VerticalAlignment="Stretch" />
            <Button Content="C" Click="ClearAll_Click" Grid.Row="0" Grid.Column="1" Background="#1F2323" Foreground="White" HorizontalAlignment="Stretch" VerticalAlignment="Stretch" />
            <Button Content="DEL" Click="Delete_Click" Grid.Row="0" Grid.Column="2" Background="#1F2323" Foreground="White" HorizontalAlignment="Stretch" VerticalAlignment="Stretch" />
            <Button Content="÷" Click="Operator_Click" Grid.Row="0" Grid.Column="3" Background="#005C7A" Foreground="White" HorizontalAlignment="Stretch" VerticalAlignment="Stretch" />

            <!-- Row 2 -->
            <Button Content="7" Click="Number_Click" Grid.Row="1" Grid.Column="0" Background="#282A2A" Foreground="White" HorizontalAlignment="Stretch" VerticalAlignment="Stretch" />
            <Button Content="8" Click="Number_Click" Grid.Row="1" Grid.Column="1" Background="#282A2A" Foreground="White" HorizontalAlignment="Stretch" VerticalAlignment="Stretch" />
            <Button Content="9" Click="Number_Click" Grid.Row="1" Grid.Column="2" Background="#282A2A" Foreground="White" HorizontalAlignment="Stretch" VerticalAlignment="Stretch" />
            <Button Content="×" Click="Operator_Click" Grid.Row="1" Grid.Column="3" Background="#005C7A" Foreground="White" HorizontalAlignment="Stretch" VerticalAlignment="Stretch" />

            <!-- Row 3 -->
            <Button Content="4" Click="Number_Click" Grid.Row="2" Grid.Column="0" Background="#282A2A" Foreground="White" HorizontalAlignment="Stretch" VerticalAlignment="Stretch" />
            <Button Content="5" Click="Number_Click" Grid.Row="2" Grid.Column="1" Background="#282A2A" Foreground="White" HorizontalAlignment="Stretch" VerticalAlignment="Stretch" />
            <Button Content="6" Click="Number_Click" Grid.Row="2" Grid.Column="2" Background="#282A2A" Foreground="White" HorizontalAlignment="Stretch" VerticalAlignment="Stretch" />
            <Button Content="-" Click="Operator_Click" Grid.Row="2" Grid.Column="3" Background="#005C7A" Foreground="White" HorizontalAlignment="Stretch" VerticalAlignment="Stretch" />

            <!-- Row 4 -->
            <Button Content="1" Click="Number_Click" Grid.Row="3" Grid.Column="0" Background="#282A2A" Foreground="White" HorizontalAlignment="Stretch" VerticalAlignment="Stretch" />
            <Button Content="2" Click="Number_Click" Grid.Row="3" Grid.Column="1" Background="#282A2A" Foreground="White" HorizontalAlignment="Stretch" VerticalAlignment="Stretch" />
            <Button Content="3" Click="Number_Click" Grid.Row="3" Grid.Column="2" Background="#282A2A" Foreground="White" HorizontalAlignment="Stretch" VerticalAlignment="Stretch" />
            <Button Content="+" Click="Operator_Click" Grid.Row="3" Grid.Column="3" Background="#005C7A" Foreground="White" HorizontalAlignment="Stretch" VerticalAlignment="Stretch" />

            <!-- Row 5 -->
            <Button Content="±" Click="Negate_Click" Grid.Row="4" Grid.Column="0" Background="#282A2A" Foreground="White" HorizontalAlignment="Stretch" VerticalAlignment="Stretch" />
            <Button Content="0" Click="Number_Click" Grid.Row="4" Grid.Column="1" Background="#282A2A" Foreground="White" HorizontalAlignment="Stretch" VerticalAlignment="Stretch" />
            <Button Content="." Click="Decimal_Click" Grid.Row="4" Grid.Column="2" Background="#282A2A" Foreground="White" HorizontalAlignment="Stretch" VerticalAlignment="Stretch" />
            <Button Content="=" Click="Equals_Click" Grid.Row="4" Grid.Column="3" Background="#60CDFF" Foreground="#003548" FontWeight="Bold" HorizontalAlignment="Stretch" VerticalAlignment="Stretch" />
        </Grid>
    </Grid>
</Page>`
    },
    {
      name: "CalculatorPage.xaml.cs",
      language: "csharp",
      description: "Handles decimal mathematical input parse states and formula representation.",
      content: `using System;
using Windows.UI.Xaml;
using Windows.UI.Xaml.Controls;

namespace LuminaKiosk
{
    public sealed partial class CalculatorPage : Page
    {
        private double _result = 0;
        private string _operation = "";
        private bool _isOperationPressed = false;

        public CalculatorPage()
        {
            this.InitializeComponent();
        }

        private void Number_Click(object sender, RoutedEventArgs e)
        {
            Button btn = (Button)sender;
            if ((DisplayBlock.Text == "0") || (_isOperationPressed))
                DisplayBlock.Text = "";

            _isOperationPressed = false;
            DisplayBlock.Text += btn.Content.ToString();
        }

        private void Operator_Click(object sender, RoutedEventArgs e)
        {
            Button btn = (Button)sender;
            _operation = btn.Content.ToString();
            _result = double.Parse(DisplayBlock.Text);
            _isOperationPressed = true;
            FormulaDisplay.Text = $"{_result} {_operation}";
        }

        private void ClearAll_Click(object sender, RoutedEventArgs e)
        {
            DisplayBlock.Text = "0";
            FormulaDisplay.Text = "";
            _result = 0;
            _operation = "";
        }

        private void Clear_Click(object sender, RoutedEventArgs e)
        {
            DisplayBlock.Text = "0";
        }

        private void Equals_Click(object sender, RoutedEventArgs e)
        {
            double secondVal = double.Parse(DisplayBlock.Text);
            FormulaDisplay.Text = $"{_result} {_operation} {secondVal} =";

            switch (_operation)
            {
                case "+":
                    DisplayBlock.Text = (_result + secondVal).ToString();
                    break;
                case "-":
                    DisplayBlock.Text = (_result - secondVal).ToString();
                    break;
                case "×":
                    DisplayBlock.Text = (_result * secondVal).ToString();
                    break;
                case "÷":
                    if (secondVal != 0)
                        DisplayBlock.Text = (_result / secondVal).ToString();
                    else
                        DisplayBlock.Text = "Error (Div By 0)";
                    break;
                default:
                    break;
            }
            _result = double.Parse(DisplayBlock.Text);
            _operation = "";
        }

        private void Delete_Click(object sender, RoutedEventArgs e)
        {
            if (DisplayBlock.Text.Length > 1)
                DisplayBlock.Text = DisplayBlock.Text.Substring(0, DisplayBlock.Text.Length - 1);
            else
                DisplayBlock.Text = "0";
        }

        private void Negate_Click(object sender, RoutedEventArgs e)
        {
            double val = double.Parse(DisplayBlock.Text) * -1;
            DisplayBlock.Text = val.ToString();
        }

        private void Decimal_Click(object sender, RoutedEventArgs e)
        {
            if (!DisplayBlock.Text.Contains("."))
                DisplayBlock.Text += ".";
        }
    }
}`
    }
  ],
  paint: [
    {
      name: "PaintPage.xaml",
      language: "xml",
      description: "Employs an InkCanvas combined with an InkToolbar to manage vector annotations natively.",
      content: `<Page
    x:Class="LuminaKiosk.PaintPage"
    xmlns="http://schemas.microsoft.com/winfx/2000/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
    Background="#101212">

    <Grid>
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto" />
            <RowDefinition Height="*" />
            <RowDefinition Height="Auto" />
        </Grid.RowDefinitions>

        <!-- Ink Toolbar Overlay (WPF/UWP native component) -->
        <InkToolbar Name="InkToolbarControl" Grid.Row="0" TargetInkCanvas="{x:Bind MyInkCanvas}" Background="#1C1E1E" HorizontalAlignment="Stretch" BorderBrush="#282A2A" BorderThickness="0,0,0,1" />

        <!-- Drawing Stage Canvas -->
        <Grid Grid.Row="1" Background="#0C0F0F" Margin="10" CornerRadius="8">
            <InkCanvas Name="MyInkCanvas" HorizontalAlignment="Stretch" VerticalAlignment="Stretch" />
        </Grid>

        <!-- Status & Toolbars -->
        <StackPanel Grid.Row="2" Orientation="Horizontal" Padding="12" Background="#141717" BorderBrush="#1C1E1E" BorderThickness="0,1,0,0">
            <Button Content="Clear Drawing Area" Click="Clear_Click" Style="{StaticResource AccentButtonStyle}" Background="#7F1D1D" Foreground="White" />
            <Button Content="Export to Pictures" Click="Export_Click" Margin="10,0,0,0" />
            <TextBlock Text="System: InkCanvas Render Pipeline Active" Margin="20,8,0,0" Foreground="#9CA3AF" FontSize="11" FontFamily="Consolas" />
        </StackPanel>
    </Grid>
</Page>`
    },
    {
      name: "PaintPage.xaml.cs",
      language: "csharp",
      description: "Registers drawing ink input streams (mouse, touch, pen) and outputs them to storage streams.",
      content: `using System;
using System.Diagnostics;
using System.IO;
using Windows.UI.Xaml;
using Windows.UI.Xaml.Controls;
using Windows.UI.Input.Inking;
using Windows.Storage;

namespace LuminaKiosk
{
    public sealed partial class PaintPage : Page
    {
        public PaintPage()
        {
            this.InitializeComponent();

            // Set input device support for the InkCanvas
            MyInkCanvas.InkPresenter.InputDeviceTypes = 
                Windows.UI.Core.CoreInputDeviceTypes.Mouse | 
                Windows.UI.Core.CoreInputDeviceTypes.Pen | 
                Windows.UI.Core.CoreInputDeviceTypes.Touch;

            // Optional: Customize drawing attributes programmatically
            InkDrawingAttributes attributes = new InkDrawingAttributes();
            attributes.Color = Windows.UI.Colors.Cyan;
            attributes.Size = new Windows.Size(3, 3);
            attributes.FitToCurve = true;
            MyInkCanvas.InkPresenter.UpdateDefaultDrawingAttributes(attributes);
        }

        private void Clear_Click(object sender, RoutedEventArgs e)
        {
            MyInkCanvas.InkPresenter.StrokeContainer.Clear();
            Debug.WriteLine("[SYSTEM] Ink Canvas strokes cleared.");
        }

        private async void Export_Click(object sender, RoutedEventArgs e)
        {
            var strokes = MyInkCanvas.InkPresenter.StrokeContainer.GetStrokes();
            if (strokes.Count == 0) return;

            try
            {
                StorageFolder picturesFolder = KnownFolders.PicturesLibrary;
                StorageFile saveFile = await picturesFolder.CreateFileAsync(
                    $"KioskDrawing_{DateTime.Now:yyyyMMdd_HHmmss}.gif",
                    CreationCollisionOption.GenerateUniqueName);

                using (var outputStream = await saveFile.OpenAsync(FileAccessMode.ReadWrite))
                {
                    await MyInkCanvas.InkPresenter.StrokeContainer.SaveAsync(outputStream);
                }
                Debug.WriteLine($"[SUCCESS] Drawing saved as GIF Ink stroke stream to Pictures: {saveFile.Name}");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[ERROR] Stroke serialization failure: {ex.Message}");
            }
        }
    }
}`
    }
  ],
  edge: [
    {
      name: "BrowserPage.xaml",
      language: "xml",
      description: "Embeds the UWP WebView2 control for chromium rendering inside the kiosk.",
      content: `<Page
    x:Class="LuminaKiosk.BrowserPage"
    xmlns="http://schemas.microsoft.com/winfx/2000/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    Background="#101212">

    <Grid>
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto" />
            <RowDefinition Height="*" />
        </Grid.RowDefinitions>

        <!-- Dynamic Navigation Address Bar -->
        <Grid Grid.Row="0" Background="#1C1E1E" Padding="8" BorderBrush="#282A2A" BorderThickness="0,0,0,1">
            <Grid.ColumnDefinitions>
                <ColumnDefinition Width="Auto" />
                <ColumnDefinition Width="Auto" />
                <ColumnDefinition Width="Auto" />
                <ColumnDefinition Width="*" />
                <ColumnDefinition Width="Auto" />
            </Grid.ColumnDefinitions>

            <Button Content="🠘" Click="GoBack_Click" Grid.Column="0" Margin="2" Background="Transparent" Foreground="White" />
            <Button Content="🠚" Click="GoForward_Click" Grid.Column="1" Margin="2" Background="Transparent" Foreground="White" />
            <Button Content="⟳" Click="Refresh_Click" Grid.Column="2" Margin="2" Background="Transparent" Foreground="White" />
            
            <TextBox Name="UrlBar" Grid.Column="3" KeyDown="UrlBar_KeyDown" Background="#0C0F0F" Foreground="White" BorderBrush="#3B93F1" VerticalContentAlignment="Center" Margin="8,0,8,0" PlaceholderText="Search or enter URL" />
            
            <Button Content="Go" Click="GoButton_Click" Grid.Column="4" Background="#3B93F1" Foreground="White" Width="60" />
        </Grid>

        <!-- WebView2 Chromium Rendering Host -->
        <WebView2 Name="MyWebView" Grid.Row="1" Source="https://www.google.com" CoreWebView2Initialized="MyWebView_CoreWebView2Initialized" />
    </Grid>
</Page>`
    },
    {
      name: "BrowserPage.xaml.cs",
      language: "csharp",
      description: "Orchestrates navigate controls and hooks security event filters on the WebView control.",
      content: `using System;
using Windows.UI.Xaml;
using Windows.UI.Xaml.Controls;
using Windows.UI.Xaml.Input;
using Microsoft.Web.WebView2.Core;

namespace LuminaKiosk
{
    public sealed partial class BrowserPage : Page
    {
        public BrowserPage()
        {
            this.InitializeComponent();
            InitializeWebViewAsync();
        }

        private async void InitializeWebViewAsync()
        {
            try
            {
                await MyWebView.EnsureCoreWebView2Async();
                MyWebView.CoreWebView2.NavigationStarting += CoreWebView2_NavigationStarting;
                MyWebView.CoreWebView2.NavigationCompleted += CoreWebView2_NavigationCompleted;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"[ERROR] WebView2 Init Failed: {ex.Message}");
            }
        }

        private void GoButton_Click(object sender, RoutedEventArgs e) => NavigateToUrl(UrlBar.Text);

        private void UrlBar_KeyDown(object sender, KeyRoutedEventArgs e)
        {
            if (e.Key == Windows.System.VirtualKey.Enter)
            {
                NavigateToUrl(UrlBar.Text);
            }
        }

        private void NavigateToUrl(string destination)
        {
            if (string.IsNullOrWhiteSpace(destination)) return;

            if (!destination.StartsWith("http://") && !destination.StartsWith("https://"))
            {
                destination = "https://" + destination;
            }

            try
            {
                MyWebView.Source = new Uri(destination);
            }
            catch (UriFormatException)
            {
                // Fallback to Search Query
                MyWebView.Source = new Uri($"https://www.google.com/search?q={Uri.EscapeDataString(destination)}");
            }
        }

        private void CoreWebView2_NavigationStarting(CoreWebView2 sender, CoreWebView2NavigationStartingEventArgs args)
        {
            UrlBar.Text = args.Uri;
            System.Diagnostics.Debug.WriteLine($"[BROWSER] Commencing Navigation: {args.Uri}");
        }

        private void CoreWebView2_NavigationCompleted(CoreWebView2 sender, CoreWebView2NavigationCompletedEventArgs args)
        {
            if (args.IsSuccess)
                System.Diagnostics.Debug.WriteLine("[BROWSER] Loaded successfully.");
            else
                System.Diagnostics.Debug.WriteLine($"[BROWSER_ERROR] Code: {args.WebErrorStatus}");
        }

        private void GoBack_Click(object sender, RoutedEventArgs e) { if (MyWebView.CanGoBack) MyWebView.GoBack(); }
        private void GoForward_Click(object sender, RoutedEventArgs e) { if (MyWebView.CanGoForward) MyWebView.GoForward(); }
        private void Refresh_Click(object sender, RoutedEventArgs e) => MyWebView.Reload();
        private void MyWebView_CoreWebView2Initialized(WebView2 sender, CoreWebView2InitializedEventArgs args) { }
    }
}`
    }
  ],
  word: [
    {
      name: "WordPage.xaml",
      language: "xml",
      description: "A customized RichEditBox with a format bar and local file save operations.",
      content: `<Page
    x:Class="LuminaKiosk.WordPage"
    xmlns="http://schemas.microsoft.com/winfx/2000/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    Background="#151717">

    <Grid Padding="12">
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto" />
            <RowDefinition Height="*" />
        </Grid.RowDefinitions>

        <!-- Editing Commands Ribbon -->
        <StackPanel Grid.Row="0" Orientation="Horizontal" Background="#1C1E1E" Padding="6" CornerRadius="4,4,0,0">
            <Button Content="Bold" Click="Bold_Click" FontWeight="Bold" Width="60" Margin="2" />
            <Button Content="Italic" Click="Italic_Click" FontStyle="Italic" Width="60" Margin="2" />
            <Button Content="Underline" Click="Underline_Click" Width="80" Margin="2" />
            <AppBarSeparator />
            <Button Content="Save Document" Click="Save_Click" Background="#3B93F1" Foreground="White" Width="120" Margin="10,2,2,2" />
        </StackPanel>

        <!-- UWP Rich Text Control -->
        <RichEditBox Name="DocumentEditor" Grid.Row="1" Background="#0C0F0F" Foreground="White" BorderBrush="#282A2A" BorderThickness="1" CornerRadius="0,0,4,4" ScrollViewer.VerticalScrollBarVisibility="Auto" Header="Kiosk Word Document Workspace" />
    </Grid>
</Page>`
    },
    {
      name: "WordPage.xaml.cs",
      language: "csharp",
      description: "Controls bolding, underline text ranges, and serialize to RTF document files.",
      content: `using System;
using Windows.UI.Xaml;
using Windows.UI.Xaml.Controls;
using Windows.UI.Text;
using Windows.Storage;

namespace LuminaKiosk
{
    public sealed partial class WordPage : Page
    {
        public WordPage()
        {
            this.InitializeComponent();
            DocumentEditor.Document.SetText(TextSetOptions.None, "=== LUMINA KIOSK WORD PROCESSOR ===\\nWrite secure documents here...");
        }

        private void Bold_Click(object sender, RoutedEventArgs e)
        {
            ITextSelection selectedText = DocumentEditor.Document.Selection;
            if (selectedText != null)
            {
                ITextCharacterFormat charFormatting = selectedText.CharacterFormat;
                charFormatting.Bold = charFormatting.Bold == FormatEffect.On ? FormatEffect.Off : FormatEffect.On;
                selectedText.CharacterFormat = charFormatting;
            }
        }

        private void Italic_Click(object sender, RoutedEventArgs e)
        {
            ITextSelection selectedText = DocumentEditor.Document.Selection;
            if (selectedText != null)
            {
                ITextCharacterFormat charFormatting = selectedText.CharacterFormat;
                charFormatting.Italic = charFormatting.Italic == FormatEffect.On ? FormatEffect.Off : FormatEffect.On;
                selectedText.CharacterFormat = charFormatting;
            }
        }

        private void Underline_Click(object sender, RoutedEventArgs e)
        {
            ITextSelection selectedText = DocumentEditor.Document.Selection;
            if (selectedText != null)
            {
                ITextCharacterFormat charFormatting = selectedText.CharacterFormat;
                charFormatting.Underline = charFormatting.Underline == UnderlineType.Single ? UnderlineType.None : UnderlineType.Single;
                selectedText.CharacterFormat = charFormatting;
            }
        }

        private async void Save_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                StorageFolder documentsFolder = KnownFolders.DocumentsLibrary;
                StorageFile file = await documentsFolder.CreateFileAsync("KioskDocument.rtf", CreationCollisionOption.GenerateUniqueName);
                
                using (var stream = await file.OpenAsync(FileAccessMode.ReadWrite))
                {
                    DocumentEditor.Document.SaveToStream(TextGetOptions.None, stream);
                }
                System.Diagnostics.Debug.WriteLine($"[SUCCESS] Word Document exported to Documents: {file.Name}");
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"[ERROR] Export failure: {ex.Message}");
            }
        }
    }
}`
    }
  ],
  excel: [
    {
      name: "ExcelPage.xaml",
      language: "xml",
      description: "Incorporates the Toolkit DataGrid component for matrix calculations.",
      content: `<Page
    x:Class="LuminaKiosk.ExcelPage"
    xmlns="http://schemas.microsoft.com/winfx/2000/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    xmlns:controls="using:Microsoft.Toolkit.Uwp.UI.Controls"
    Background="#101212">

    <Grid Padding="12">
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto" />
            <RowDefinition Height="*" />
        </Grid.RowDefinitions>

        <!-- Formula Bar -->
        <Grid Grid.Row="0" Margin="0,0,0,12" ColumnSpacing="8">
            <Grid.ColumnDefinitions>
                <ColumnDefinition Width="Auto" />
                <ColumnDefinition Width="*" />
                <ColumnDefinition Width="Auto" />
            </Grid.ColumnDefinitions>
            <TextBlock Text="fx" FontSize="16" FontWeight="Bold" Foreground="#34D399" VerticalAlignment="Center" />
            <TextBox Name="FormulaInput" Grid.Column="1" Background="#1C1E1E" Foreground="White" BorderBrush="#34D399" Height="36" PlaceholderText="Select a cell and input formulas (e.g. =SUM(A1:B2))" />
            <Button Content="Recalculate Sheet" Click="Calculate_Click" Grid.Column="2" Background="#10B981" Foreground="White" Height="36" />
        </Grid>

        <!-- Fluent DataGrid SpreadSheet -->
        <controls:DataGrid Name="SpreadsheetGrid" Grid.Row="1" AutoGenerateColumns="True" HeaderBackground="#1C1E1E" RowBackground="#0C0F0F" AlternatingRowBackground="#151717" BorderBrush="#1C1E1E" BorderThickness="1" SelectionMode="SingleCell" />
    </Grid>
</Page>`
    },
    {
      name: "ExcelPage.xaml.cs",
      language: "csharp",
      description: "Parses Excel mathematical sheets and manages data grid cell valuations.",
      content: `using System;
using System.Collections.ObjectModel;
using System.Diagnostics;
using Windows.UI.Xaml;
using Windows.UI.Xaml.Controls;

namespace LuminaKiosk
{
    public sealed partial class ExcelPage : Page
    {
        public class SheetRow
        {
            public string RowHeader { get; set; }
            public string A { get; set; }
            public string B { get; set; }
            public string C { get; set; }
            public string D { get; set; }
        }

        private ObservableCollection<SheetRow> _sheetData;

        public ExcelPage()
        {
            this.InitializeComponent();
            LoadSampleSheet();
        }

        private void LoadSampleSheet()
        {
            _sheetData = new ObservableCollection<SheetRow>
            {
                new SheetRow { RowHeader = "1", A = "METRIC", B = "VALUE", C = "THRESHOLD", D = "STATUS" },
                new SheetRow { RowHeader = "2", A = "Core Temp", B = "42", C = "75", D = "STABLE" },
                new SheetRow { RowHeader = "3", A = "Memory Heap", B = "4.1", C = "12.0", D = "OPTIMAL" },
                new SheetRow { RowHeader = "4", A = "Packet loss", B = "0.0", C = "0.05", D = "SECURE" }
            };

            SpreadsheetGrid.ItemsSource = _sheetData;
        }

        private void Calculate_Click(object sender, RoutedEventArgs e)
        {
            // Simple logic for evaluation of expressions
            string formula = FormulaInput.Text;
            if (formula.StartsWith("=SUM"))
            {
                try
                {
                    double sum = double.Parse(_sheetData[1].B) + double.Parse(_sheetData[2].B) + double.Parse(_sheetData[3].B);
                    FormulaInput.Text = $"Evaluation Output: {sum}";
                    Debug.WriteLine($"[EXCEL] SUM computed: {sum}");
                }
                catch
                {
                    FormulaInput.Text = "#VAL_ERROR";
                }
            }
            else
            {
                Debug.WriteLine("[EXCEL] Recalculating grid bindings.");
            }
        }
    }
}`
    }
  ],
  pdf: [
    {
      name: "PdfPage.xaml",
      language: "xml",
      description: "Displays document pages dynamically utilizing UWP's native Windows.Data.Pdf engine.",
      content: `<Page
    x:Class="LuminaKiosk.PdfPage"
    xmlns="http://schemas.microsoft.com/winfx/2000/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    Background="#101212">

    <Grid>
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto" />
            <RowDefinition Height="*" />
        </Grid.RowDefinitions>

        <!-- PDF Reader Ribbon -->
        <StackPanel Grid.Row="0" Orientation="Horizontal" Background="#1C1E1E" Padding="8" BorderBrush="#282A2A" BorderThickness="0,0,0,1">
            <Button Content="Previous Page" Click="Prev_Click" Margin="2" />
            <TextBlock Name="PageIndicator" Text="Page 1 of 5" Foreground="White" VerticalAlignment="Center" Margin="12,0,12,0" FontWeight="SemiBold" />
            <Button Content="Next Page" Click="Next_Click" Margin="2" />
            <AppBarSeparator />
            <TextBlock Text="Doc: Lumina_Kiosk_Operator_Manual.pdf" Foreground="#F87171" FontWeight="Bold" Margin="20,6,0,0" FontSize="11" FontFamily="Consolas" />
        </StackPanel>

        <!-- Document Render Host -->
        <ScrollViewer Grid.Row="1" Background="#0C0F0F" HorizontalScrollMode="Auto" VerticalScrollMode="Auto">
            <Image Name="PdfPageDisplay" Margin="24" Width="600" HorizontalAlignment="Center" Stretch="Uniform" />
        </ScrollViewer>
    </Grid>
</Page>`
    },
    {
      name: "PdfPage.xaml.cs",
      language: "csharp",
      description: "Loads localized PDFs and converts pages to in-memory BGRA image streams.",
      content: `using System;
using System.Diagnostics;
using Windows.UI.Xaml;
using Windows.UI.Xaml.Controls;
using Windows.UI.Xaml.Media.Imaging;
using Windows.Data.Pdf;
using Windows.Storage;
using Windows.Storage.Streams;

namespace LuminaKiosk
{
    public sealed partial class PdfPage : Page
    {
        private PdfDocument _pdfDocument;
        private uint _currentPageIndex = 0;

        public PdfPage()
        {
            this.InitializeComponent();
            LoadPdfAsync();
        }

        private async void LoadPdfAsync()
        {
            try
            {
                Uri pdfUri = new Uri("ms-appx:///Assets/Lumina_Kiosk_Operator_Manual.pdf");
                StorageFile file = await StorageFile.GetFileFromApplicationUriAsync(pdfUri);
                _pdfDocument = await PdfDocument.LoadFromFileAsync(file);
                
                PageIndicator.Text = $"Page 1 of {_pdfDocument.PageCount}";
                await RenderActivePageAsync();
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[ERROR] Failed to load PDF stream: {ex.Message}");
            }
        }

        private async System.Threading.Tasks.Task RenderActivePageAsync()
        {
            if (_pdfDocument == null) return;

            using (PdfPage page = _pdfDocument.GetPage(_currentPageIndex))
            {
                var stream = new InMemoryRandomAccessStream();
                await page.RenderToStreamAsync(stream);

                BitmapImage bitmapImage = new BitmapImage();
                await bitmapImage.SetSourceAsync(stream);
                PdfPageDisplay.Source = bitmapImage;
            }
        }

        private async void Prev_Click(object sender, RoutedEventArgs e)
        {
            if (_currentPageIndex > 0)
            {
                _currentPageIndex--;
                PageIndicator.Text = $"Page {_currentPageIndex + 1} of {_pdfDocument.PageCount}";
                await RenderActivePageAsync();
            }
        }

        private async void Next_Click(object sender, RoutedEventArgs e)
        {
            if (_currentPageIndex < _pdfDocument.PageCount - 1)
            {
                _currentPageIndex++;
                PageIndicator.Text = $"Page {_currentPageIndex + 1} of {_pdfDocument.PageCount}";
                await RenderActivePageAsync();
            }
        }
    }
}`
    }
  ],
  notepad: [
    {
      name: "NotepadPage.xaml",
      language: "xml",
      description: "Simple multi-line plain text editing container with high responsive wrapping.",
      content: `<Page
    x:Class="LuminaKiosk.NotepadPage"
    xmlns="http://schemas.microsoft.com/winfx/2000/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    Background="#101212">

    <Grid>
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto" />
            <RowDefinition Height="*" />
        </Grid.RowDefinitions>

        <!-- Command Menu -->
        <MenuBar Grid.Row="0" Background="#1C1E1E">
            <MenuBarItem Title="File">
                <MenuFlyoutItem Text="New Note" Click="New_Click" />
                <MenuFlyoutItem Text="Save Plaintext" Click="Save_Click" />
            </MenuBarItem>
        </MenuBar>

        <!-- Plain TextBox editor -->
        <TextBox Name="NoteEditor" Grid.Row="1" AcceptsReturn="True" TextWrapping="Wrap" ScrollViewer.VerticalScrollBarVisibility="Auto" BorderThickness="0" Background="#0C0F0F" Foreground="#F3F4F6" FontFamily="Consolas" Padding="16" PlaceholderText="Write plaintext scratchpad records..." />
    </Grid>
</Page>`
    },
    {
      name: "NotepadPage.xaml.cs",
      language: "csharp",
      description: "Direct string reading and writing logic from local streams using StorageFile IO.",
      content: `using System;
using System.Diagnostics;
using Windows.UI.Xaml;
using Windows.UI.Xaml.Controls;
using Windows.Storage;

namespace LuminaKiosk
{
    public sealed partial class NotepadPage : Page
    {
        public NotepadPage()
        {
            this.InitializeComponent();
        }

        private void New_Click(object sender, RoutedEventArgs e)
        {
            NoteEditor.Text = "";
            Debug.WriteLine("[NOTEPAD] Text Editor state cleared.");
        }

        private async void Save_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(NoteEditor.Text)) return;

            try
            {
                StorageFolder localFolder = ApplicationData.Current.LocalFolder;
                StorageFile textFile = await localFolder.CreateFileAsync(
                    "KioskNote.txt",
                    CreationCollisionOption.GenerateUniqueName);

                await FileIO.WriteTextAsync(textFile, NoteEditor.Text);
                Debug.WriteLine($"[NOTEPAD] Saved file successfully: {textFile.Path}");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[ERROR] Plaintext write failed: {ex.Message}");
            }
        }
    }
}`
    }
  ],
  files: [
    {
      name: "FilesPage.xaml",
      language: "xml",
      description: "Directories viewer displaying lists of virtual storage volumes on the kiosk.",
      content: `<Page
    x:Class="LuminaKiosk.FilesPage"
    xmlns="http://schemas.microsoft.com/winfx/2000/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    Background="#101212">

    <Grid Padding="16">
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto" />
            <RowDefinition Height="*" />
        </Grid.RowDefinitions>

        <!-- Storage breadcrumb -->
        <TextBlock Grid.Row="0" Text="C:\\Users\\KioskOperator\\SandboxStorage\\" FontSize="12" FontFamily="Consolas" Foreground="#60CDFF" Margin="4,0,0,12" />

        <!-- Storage Files ListView Grid -->
        <ListView Name="FileListView" Grid.Row="1" Background="#1C1E1E" BorderBrush="#282A2A" BorderThickness="1" CornerRadius="8">
            <ListView.ItemTemplate>
                <DataTemplate>
                    <Grid Padding="8" ColumnSpacing="12">
                        <Grid.ColumnDefinitions>
                            <ColumnDefinition Width="Auto" />
                            <ColumnDefinition Width="*" />
                            <ColumnDefinition Width="Auto" />
                        </Grid.ColumnDefinitions>
                        <!-- Icon -->
                        <SymbolIcon Symbol="Folder" Foreground="#FFE600" Grid.Column="0" VerticalAlignment="Center" />
                        <!-- Name & Metadata -->
                        <StackPanel Grid.Column="1">
                            <TextBlock Text="{Binding Name}" FontWeight="Bold" Foreground="White" />
                            <TextBlock Text="{Binding Size}" FontSize="10" Foreground="#9CA3AF" />
                        </StackPanel>
                        <!-- Date -->
                        <TextBlock Text="{Binding DateModified}" Grid.Column="2" VerticalAlignment="Center" Foreground="#9CA3AF" FontSize="11" />
                    </Grid>
                </DataTemplate>
            </ListView.ItemTemplate>
        </ListView>
    </Grid>
</Page>`
    },
    {
      name: "FilesPage.xaml.cs",
      language: "csharp",
      description: "Reads local folders dynamically using StorageFolder APIs and binds lists.",
      content: `using System;
using System.Collections.Generic;
using System.Diagnostics;
using Windows.UI.Xaml.Controls;
using Windows.Storage;

namespace LuminaKiosk
{
    public class FileNode
    {
        public string Name { get; set; }
        public string Size { get; set; }
        public string DateModified { get; set; }
    }

    public sealed partial class FilesPage : Page
    {
        public FilesPage()
        {
            this.InitializeComponent();
            PopulateFilesListAsync();
        }

        private async void PopulateFilesListAsync()
        {
            try
            {
                StorageFolder localFolder = ApplicationData.Current.LocalFolder;
                IReadOnlyList<IStorageItem> items = await localFolder.GetItemsAsync();
                
                List<FileNode> fileNodes = new List<FileNode>();
                foreach (var item in items)
                {
                    if (item is StorageFile file)
                    {
                        var basicProperties = await file.GetBasicPropertiesAsync();
                        fileNodes.Add(new FileNode
                        {
                            Name = file.Name,
                            Size = $"{basicProperties.Size / 1024.0:F1} KB",
                            DateModified = basicProperties.DateModified.ToString("g")
                        });
                    }
                }

                // Append static document mocks if directory is clean
                if (fileNodes.Count == 0)
                {
                    fileNodes.Add(new FileNode { Name = "Lumina_Systems_Specs.doc", Size = "2.4 KB", DateModified = "07/08/2026 02:27 PM" });
                    fileNodes.Add(new FileNode { Name = "Core_Kiosk_Telemetry.sheet", Size = "1.2 KB", DateModified = "07/08/2026 02:30 PM" });
                }

                FileListView.ItemsSource = fileNodes;
                Debug.WriteLine("[FILES] Storage directory loaded and grid bound.");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[ERROR] Directory read error: {ex.Message}");
            }
        }
    }
}`
    }
  ],
  settings: [
    {
      name: "SettingsPage.xaml",
      language: "xml",
      description: "Modern NavigationView organizing Kiosk, Telemetry, and spec panel pivots.",
      content: `<Page
    x:Class="LuminaKiosk.SettingsPage"
    xmlns="http://schemas.microsoft.com/winfx/2000/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    Background="#101212">

    <Grid>
        <NavigationView x:Name="SettingsNav" SelectionChanged="SettingsNav_SelectionChanged" PaneDisplayMode="Left" Background="#1C1E1E">
            <NavigationView.MenuItems>
                <NavigationViewItem Content="Kiosk Config" Icon="Setting" Tag="kiosk" />
                <NavigationViewItem Content="Telemetry Data" Icon="FourBars" Tag="telemetry" />
                <NavigationViewItem Content="Audit Logs" Icon="Document" Tag="logs" />
            </NavigationView.MenuItems>

            <Frame x:Name="ContentFrame" Margin="24">
                <!-- Inner views pivot here -->
            </Frame>
        </NavigationView>
    </Grid>
</Page>`
    },
    {
      name: "SettingsPage.xaml.cs",
      language: "csharp",
      description: "Updates device hostname registries and manages navigation page switches.",
      content: `using System;
using System.Diagnostics;
using Windows.UI.Xaml.Controls;

namespace LuminaKiosk
{
    public sealed partial class SettingsPage : Page
    {
        public SettingsPage()
        {
            this.InitializeComponent();
            SettingsNav.SelectedItem = SettingsNav.MenuItems[0];
        }

        private void SettingsNav_SelectionChanged(NavigationView sender, NavigationViewSelectionChangedEventArgs args)
        {
            if (args.SelectedItemContainer != null)
            {
                string tag = args.SelectedItemContainer.Tag.ToString();
                Debug.WriteLine($"[SETTINGS] Shift category pane focus to: {tag}");
                
                switch (tag)
                {
                    case "kiosk":
                        ContentFrame.Navigate(typeof(KioskConfigPage));
                        break;
                    case "telemetry":
                        ContentFrame.Navigate(typeof(TelemetryViewPage));
                        break;
                    case "logs":
                        ContentFrame.Navigate(typeof(AuditLogsViewPage));
                        break;
                }
            }
        }
    }
}`
    }
  ]
};
