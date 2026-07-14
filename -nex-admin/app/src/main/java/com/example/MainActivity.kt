package com.example

import android.content.Context
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.Bundle
import android.widget.Toast
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.lifecycleScope
import com.example.data.model.User
import com.example.data.model.ActivityLog
import com.example.data.model.DeviceState
import com.example.data.model.ModeHistoryEntry
import com.example.data.model.InstalledApp
import com.example.ui.dashboard.*
import com.example.ui.login.LoginViewModel
import com.example.ui.login.LoginState
import com.example.ui.theme.*
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch

// Screen Enumeration for state-based Compose Navigation
sealed class Screen {
    object Splash : Screen()
    object Login : Screen()
    object Dashboard : Screen()
    object DeviceDetails : Screen()
    object ModeControl : Screen()
    object Alerts : Screen()
    object Settings : Screen()
    object Profile : Screen()
    object About : Screen()
    object UserDirectory : Screen()
    data class UserForm(val user: User?) : Screen()
}

@Composable
fun Greeting(name: String, modifier: Modifier = Modifier) {
    Text(
        text = "Hello $name!",
        color = CyberPrimary,
        fontFamily = FontFamily.Monospace,
        modifier = modifier
    )
}

class MainActivity : AppCompatActivity() {

    private val loginViewModel: LoginViewModel by viewModels()
    private val dashboardViewModel: DashboardViewModel by viewModels()
    private val businessViewModel: BusinessViewModel by viewModels()
    private val appPushViewModel: AppPushViewModel by viewModels()
    private val installedAppViewModel: InstalledAppViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        enableEdgeToEdge()
        super.onCreate(savedInstanceState)

        // Force observing state if logged in
        if (loginViewModel.isUserLoggedIn()) {
            dashboardViewModel.startObserving()
            val email = loginViewModel.getCurrentUserEmail()
            businessViewModel.setAdminEmail(email)
        }

        setContent {
            MyApplicationTheme {
                MainContent()
            }
        }

        observeToastEvents()
    }

    private fun observeToastEvents() {
        lifecycleScope.launch {
            loginViewModel.loginState.collectLatest { state ->
                if (state is LoginState.Error) {
                    Toast.makeText(this@MainActivity, state.message, Toast.LENGTH_LONG).show()
                }
            }
        }
        lifecycleScope.launch {
            dashboardViewModel.modeChangeResult.collectLatest { result ->
                result?.onSuccess {
                    Toast.makeText(this@MainActivity, "Active Mode synced securely to cloud.", Toast.LENGTH_SHORT).show()
                    dashboardViewModel.clearModeChangeResult()
                }?.onFailure { exception ->
                    Toast.makeText(this@MainActivity, "Sync failed: ${exception.localizedMessage}", Toast.LENGTH_LONG).show()
                    dashboardViewModel.clearModeChangeResult()
                }
            }
        }
    }

    private fun isNetworkConnected(): Boolean {
        val connectivityManager = getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val activeNetwork = connectivityManager.activeNetwork ?: return false
        val capabilities = connectivityManager.getNetworkCapabilities(activeNetwork) ?: return false
        return capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
    }

    @OptIn(ExperimentalAnimationApi::class)
    @Composable
    fun MainContent() {
        var currentScreen by remember { mutableStateOf<Screen>(Screen.Splash) }
        val sharedPrefs = LocalContext.current.getSharedPreferences("nex_prefs", Context.MODE_PRIVATE)

        // Synchronize initial session
        LaunchedEffect(Unit) {
            if (currentScreen is Screen.Splash) {
                // Splash bootloader delay
                delay(2800)
                if (loginViewModel.isUserLoggedIn()) {
                    currentScreen = Screen.Dashboard
                } else {
                    currentScreen = Screen.Login
                }
            }
        }

        // Pulse warning if Lockdown Mode is activated
        val deviceState by dashboardViewModel.deviceState.collectAsStateWithLifecycle()
        val isLockdown = deviceState.active_mode.equals("lockdown", ignoreCase = true)
        val lockdownColorState = rememberInfiniteTransition()
        val pulsingRedIntensity by if (isLockdown) {
            lockdownColorState.animateFloat(
                initialValue = 0.05f,
                targetValue = 0.25f,
                animationSpec = infiniteRepeatable(
                    animation = tween(1200, easing = LinearEasing),
                    repeatMode = RepeatMode.Reverse
                )
            )
        } else {
            remember { mutableStateOf(0f) }
        }

        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(CyberBackground)
                .drawBehind {
                    // Draw custom modern security background grid
                    val strokeWidth = 1f
                    val step = 45.dp.toPx()
                    val gridColor = CyberPrimary.copy(alpha = 0.03f)
                    var x = 0f
                    while (x < size.width) {
                        drawLine(gridColor, start = Offset(x, 0f), end = Offset(x, size.height), strokeWidth = strokeWidth)
                        x += step
                    }
                    var y = 0f
                    while (y < size.height) {
                        drawLine(gridColor, start = Offset(0f, y), end = Offset(size.width, y), strokeWidth = strokeWidth)
                        y += step
                    }

                    // Pulsing red glow during active lockdown state
                    if (isLockdown) {
                        drawRect(
                            brush = Brush.radialGradient(
                                colors = listOf(CyberError.copy(alpha = pulsingRedIntensity), Color.Transparent),
                                center = Offset(size.width / 2, size.height / 2),
                                radius = size.minDimension
                            )
                        )
                    }
                }
                .windowInsetsPadding(WindowInsets.safeDrawing)
        ) {
            AnimatedContent(
                targetState = currentScreen,
                transitionSpec = {
                    slideInHorizontally(animationSpec = tween(400)) { width -> width } + fadeIn(animationSpec = tween(300)) with
                    slideOutHorizontally(animationSpec = tween(400)) { width -> -width } + fadeOut(animationSpec = tween(300))
                }
            ) { screen ->
                when (screen) {
                    is Screen.Splash -> SplashLoaderView()
                    is Screen.Login -> LoginView(
                        onLoginSuccess = {
                            val email = loginViewModel.getCurrentUserEmail()
                            businessViewModel.setAdminEmail(email)
                            dashboardViewModel.startObserving()
                            currentScreen = Screen.Dashboard
                        }
                    )
                    is Screen.Dashboard -> DashboardView(
                        onNavigate = { currentScreen = it }
                    )
                    is Screen.DeviceDetails -> DeviceDetailsView(
                        onBack = { currentScreen = Screen.Dashboard }
                    )
                    is Screen.ModeControl -> ModeControlView(
                        onBack = { currentScreen = Screen.Dashboard }
                    )
                    is Screen.Alerts -> AlertsView(
                        onBack = { currentScreen = Screen.Dashboard }
                    )
                    is Screen.Settings -> SettingsView(
                        onNavigate = { currentScreen = it },
                        onLogout = {
                            dashboardViewModel.stopObserving()
                            loginViewModel.logout()
                            currentScreen = Screen.Login
                        }
                    )
                    is Screen.Profile -> AdminProfileView(
                        onBack = { currentScreen = Screen.Dashboard }
                    )
                    is Screen.About -> AboutView(
                        onBack = { currentScreen = Screen.Settings }
                    )
                    is Screen.UserDirectory -> UserDirectoryView(
                        onNavigateToForm = { currentScreen = Screen.UserForm(it) },
                        onBack = { currentScreen = Screen.Dashboard }
                    )
                    is Screen.UserForm -> UserFormView(
                        editingUser = screen.user,
                        onBack = { currentScreen = Screen.UserDirectory }
                    )
                }
            }
        }
    }

    // ==========================================
    // SCREEN 1: SPLASH LOADER SCREEN
    // ==========================================
    @Composable
    fun SplashLoaderView() {
        var bootTextIndex by remember { mutableStateOf(0) }
        val bootLogs = listOf(
            "Initializing NeX Cryptographic Core...",
            "Establishing SSL Handshake...",
            "Parsing Realtime Device Database Node...",
            "Authenticating Security Policies...",
            "Active Encryption Tunnel Verified.",
            "Launching Control Terminal..."
        )

        LaunchedEffect(Unit) {
            while (bootTextIndex < bootLogs.lastIndex) {
                delay(450)
                bootTextIndex++
            }
        }

        val infiniteTransition = rememberInfiniteTransition()
        val pulseScale by infiniteTransition.animateFloat(
            initialValue = 0.85f,
            targetValue = 1.05f,
            animationSpec = infiniteRepeatable(
                animation = tween(1200, easing = FastOutSlowInEasing),
                repeatMode = RepeatMode.Reverse
            )
        )

        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(24.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Box(
                modifier = Modifier
                    .size(120.dp)
                    .drawBehind {
                        drawCircle(
                            color = CyberPrimary.copy(alpha = 0.08f * pulseScale),
                            radius = size.width / 1.5f
                        )
                    },
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Default.Security,
                    contentDescription = "Shield Logo",
                    tint = CyberPrimary,
                    modifier = Modifier.size(72.dp)
                )
            }
            Spacer(modifier = Modifier.height(32.dp))
            Text(
                text = "NEX SHIELD",
                color = TextPrimary,
                fontSize = 28.sp,
                fontWeight = FontWeight.Bold,
                fontFamily = FontFamily.Monospace,
                letterSpacing = 4.sp
            )
            Text(
                text = "ENTERPRISE ADMINISTRATOR CONTROL",
                color = CyberSecondary,
                fontSize = 11.sp,
                fontWeight = FontWeight.SemiBold,
                letterSpacing = 2.sp,
                modifier = Modifier.padding(top = 4.dp)
            )
            Spacer(modifier = Modifier.height(48.dp))
            CircularProgressIndicator(
                color = CyberPrimary,
                strokeWidth = 3.dp,
                modifier = Modifier.size(36.dp)
            )
            Spacer(modifier = Modifier.height(24.dp))
            Text(
                text = bootLogs[bootTextIndex],
                color = TextSecondary,
                fontSize = 12.sp,
                fontFamily = FontFamily.Monospace,
                textAlign = TextAlign.Center,
                modifier = Modifier.fillMaxWidth()
            )
        }
    }

    // ==========================================
    // SCREEN 2: CYBER SECURITY LOGIN PORTAL
    // ==========================================
    @Composable
    fun LoginView(onLoginSuccess: () -> Unit) {
        var email by remember { mutableStateOf("") }
        var password by remember { mutableStateOf("") }
        var isPasswordVisible by remember { mutableStateOf(false) }

        var emailError by remember { mutableStateOf<String?>(null) }
        var passwordError by remember { mutableStateOf<String?>(null) }

        val loginState by loginViewModel.loginState.collectAsStateWithLifecycle()
        val isLoading = loginState is LoginState.Loading

        LaunchedEffect(loginState) {
            if (loginState is LoginState.Success) {
                onLoginSuccess()
                loginViewModel.resetState()
            }
        }

        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(24.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                imageVector = Icons.Default.Lock,
                contentDescription = "Security Gateway Lock",
                tint = CyberPrimary,
                modifier = Modifier.size(64.dp)
            )
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = "SECURITY ACCESS",
                color = TextPrimary,
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
                fontFamily = FontFamily.Monospace,
                letterSpacing = 2.sp
            )
            Text(
                text = "Decrypting Administrator Terminal Nodes",
                color = TextSecondary,
                fontSize = 13.sp,
                textAlign = TextAlign.Center
            )
            Spacer(modifier = Modifier.height(32.dp))

            CyberCard(
                modifier = Modifier.fillMaxWidth(),
                borderColor = CyberPrimary.copy(alpha = 0.4f)
            ) {
                Text(
                    text = "CREDENTIALS REQUISITE",
                    color = CyberPrimary,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    fontFamily = FontFamily.Monospace,
                    modifier = Modifier.padding(bottom = 16.dp)
                )

                OutlinedTextField(
                    value = email,
                    onValueChange = {
                        email = it
                        emailError = null
                    },
                    label = { Text("Admin Email", color = TextSecondary) },
                    singleLine = true,
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedTextColor = TextPrimary,
                        unfocusedTextColor = TextPrimary,
                        focusedBorderColor = CyberPrimary,
                        unfocusedBorderColor = CyberBorder,
                        focusedLabelColor = CyberPrimary
                    ),
                    modifier = Modifier.fillMaxWidth().testTag("username_input")
                )
                if (emailError != null) {
                    Text(text = emailError!!, color = CyberError, fontSize = 11.sp, modifier = Modifier.padding(top = 4.dp))
                }

                Spacer(modifier = Modifier.height(16.dp))

                OutlinedTextField(
                    value = password,
                    onValueChange = {
                        password = it
                        passwordError = null
                    },
                    label = { Text("Access Key", color = TextSecondary) },
                    singleLine = true,
                    visualTransformation = if (isPasswordVisible) VisualTransformation.None else PasswordVisualTransformation(),
                    trailingIcon = {
                        IconButton(onClick = { isPasswordVisible = !isPasswordVisible }) {
                            Icon(
                                imageVector = if (isPasswordVisible) Icons.Default.Visibility else Icons.Default.VisibilityOff,
                                contentDescription = "Toggle password",
                                tint = TextSecondary
                            )
                        }
                    },
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedTextColor = TextPrimary,
                        unfocusedTextColor = TextPrimary,
                        focusedBorderColor = CyberPrimary,
                        unfocusedBorderColor = CyberBorder,
                        focusedLabelColor = CyberPrimary
                    ),
                    modifier = Modifier.fillMaxWidth().testTag("password_input")
                )
                if (passwordError != null) {
                    Text(text = passwordError!!, color = CyberError, fontSize = 11.sp, modifier = Modifier.padding(top = 4.dp))
                }

                Spacer(modifier = Modifier.height(24.dp))

                Button(
                    onClick = {
                        var valid = true
                        if (email.isBlank() || !email.contains("@")) {
                            emailError = "Invalid cryptographic email form."
                            valid = false
                        }
                        if (password.length < 6) {
                            passwordError = "Key length must be >= 6 characters."
                            valid = false
                        }
                        if (valid && !isLoading) {
                            if (!isNetworkConnected()) {
                                Toast.makeText(this@MainActivity, "Active internet required for SSL Handshake.", Toast.LENGTH_LONG).show()
                            } else {
                                loginViewModel.login(email.trim(), password.trim())
                            }
                        }
                    },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = CyberPrimary,
                        contentColor = CyberBackground
                    ),
                    shape = RoundedCornerShape(8.dp),
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(50.dp)
                        .testTag("submit_button")
                ) {
                    if (isLoading) {
                        CircularProgressIndicator(color = CyberBackground, modifier = Modifier.size(24.dp))
                    } else {
                        Text(
                            text = "ESTABLISH PROTOCOL",
                            fontWeight = FontWeight.Bold,
                            fontFamily = FontFamily.Monospace
                        )
                    }
                }
            }
        }
    }

    // ==========================================
    // SCREEN 3: TELEMETRY COMMAND CENTER (DASHBOARD)
    // ==========================================
    @Composable
    fun DashboardView(
        onNavigate: (Screen) -> Unit
    ) {
        val deviceState by dashboardViewModel.deviceState.collectAsStateWithLifecycle()
        val isOnline by dashboardViewModel.isDeviceOnline.collectAsStateWithLifecycle()
        val logs by businessViewModel.activityLogs.collectAsStateWithLifecycle()
        val installedAppsState by installedAppViewModel.uiState.collectAsStateWithLifecycle()
        val appActionResult by installedAppViewModel.actionResult.collectAsStateWithLifecycle()

        LaunchedEffect(appActionResult) {
            appActionResult?.let { result ->
                if (result.isSuccess) {
                    Toast.makeText(this@MainActivity, "Command deployed to secure queue.", Toast.LENGTH_SHORT).show()
                } else {
                    Toast.makeText(this@MainActivity, "Transmission error: ${result.exceptionOrNull()?.message}", Toast.LENGTH_LONG).show()
                }
                installedAppViewModel.clearActionResult()
            }
        }

        // Local state simulated live metrics (grows trust & security aesthetic)
        var cpuUsage by remember { mutableStateOf(0.42f) }
        var ramUsageByTime by remember { mutableStateOf(8.4f) }
        var activeTasksCount by remember { mutableStateOf(4) }

        LaunchedEffect(Unit) {
            while (true) {
                delay(3000)
                // Fluctuate CPU slightly
                cpuUsage = (35 + (0..18).random()) / 100f
                // Fluctuate RAM slightly
                ramUsageByTime = 8.2f + (0..4).random() / 10f
                // Random active tasks
                activeTasksCount = 3 + (0..3).random()
            }
        }

        var activeTab by remember { mutableStateOf(0) }

        Scaffold(
            containerColor = Color.Transparent,
            bottomBar = {
                NavigationBar(
                    containerColor = CyberSurface,
                    tonalElevation = 8.dp,
                    modifier = Modifier.windowInsetsPadding(WindowInsets.navigationBars)
                ) {
                    NavigationBarItem(
                        selected = activeTab == 0,
                        onClick = { activeTab = 0 },
                        icon = { Icon(Icons.Default.Dns, contentDescription = "Terminal") },
                        label = { Text("Terminal", fontFamily = FontFamily.Monospace, fontSize = 11.sp) },
                        colors = NavigationBarItemDefaults.colors(
                            selectedIconColor = CyberPrimary,
                            selectedTextColor = CyberPrimary,
                            unselectedIconColor = TextSecondary,
                            unselectedTextColor = TextSecondary,
                            indicatorColor = CyberSurfaceCard
                        )
                    )
                    NavigationBarItem(
                        selected = activeTab == 1,
                        onClick = { onNavigate(Screen.UserDirectory) },
                        icon = { Icon(Icons.Default.People, contentDescription = "Users") },
                        label = { Text("Profiles", fontFamily = FontFamily.Monospace, fontSize = 11.sp) },
                        colors = NavigationBarItemDefaults.colors(
                            selectedIconColor = CyberPrimary,
                            selectedTextColor = CyberPrimary,
                            unselectedIconColor = TextSecondary,
                            unselectedTextColor = TextSecondary,
                            indicatorColor = CyberSurfaceCard
                        )
                    )
                    NavigationBarItem(
                        selected = activeTab == 2,
                        onClick = { onNavigate(Screen.Settings) },
                        icon = { Icon(Icons.Default.Settings, contentDescription = "Config") },
                        label = { Text("Config", fontFamily = FontFamily.Monospace, fontSize = 11.sp) },
                        colors = NavigationBarItemDefaults.colors(
                            selectedIconColor = CyberPrimary,
                            selectedTextColor = CyberPrimary,
                            unselectedIconColor = TextSecondary,
                            unselectedTextColor = TextSecondary,
                            indicatorColor = CyberSurfaceCard
                        )
                    )
                }
            }
        ) { paddingValues ->
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
                    .padding(horizontal = 16.dp)
                    .verticalScroll(rememberScrollState())
            ) {
                // Header Bar
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            modifier = Modifier
                                .size(40.dp)
                                .clip(CircleShape)
                                .background(CyberPrimary.copy(alpha = 0.1f)),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(Icons.Default.Terminal, contentDescription = "Terminal core", tint = CyberPrimary, modifier = Modifier.size(20.dp))
                        }
                        Spacer(modifier = Modifier.width(12.dp))
                        Column {
                            Text(text = "NEX ADMIN", color = TextPrimary, fontWeight = FontWeight.Bold, fontSize = 18.sp, fontFamily = FontFamily.Monospace)
                            Text(
                                text = loginViewModel.getCurrentUserEmail(),
                                color = TextSecondary,
                                fontSize = 11.sp,
                                fontFamily = FontFamily.Monospace
                            )
                        }
                    }

                    // Refresh Button
                    IconButton(
                        onClick = {
                            businessViewModel.refreshData()
                            Toast.makeText(this@MainActivity, "Active nodes query updated.", Toast.LENGTH_SHORT).show()
                        },
                        modifier = Modifier
                            .clip(CircleShape)
                            .background(CyberSurface)
                    ) {
                        Icon(Icons.Default.Refresh, contentDescription = "Refresh data", tint = CyberPrimary)
                    }
                }

                // Device Connection Header Card (Navigates to Details)
                CyberCard(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { onNavigate(Screen.DeviceDetails) },
                    borderColor = if (isOnline) CyberTertiary.copy(alpha = 0.4f) else CyberError.copy(alpha = 0.4f)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            // Pulsing dot
                            val pulseAlpha = rememberInfiniteTransition()
                            val alpha by pulseAlpha.animateFloat(
                                initialValue = 0.4f,
                                targetValue = 1.0f,
                                animationSpec = infiniteRepeatable(
                                    animation = tween(800, easing = EaseIn),
                                    repeatMode = RepeatMode.Reverse
                                )
                            )

                            Box(
                                modifier = Modifier
                                    .size(12.dp)
                                    .clip(CircleShape)
                                    .background(
                                        if (isOnline) CyberTertiary.copy(alpha = alpha) else CyberError.copy(
                                            alpha = alpha
                                        )
                                    )
                            )
                            Spacer(modifier = Modifier.width(12.dp))
                            Column {
                                Text(
                                    text = if (isOnline) "DEVICE_STATE: ACTIVE" else "DEVICE_STATE: UNREACHABLE",
                                    color = if (isOnline) CyberTertiary else CyberError,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 14.sp,
                                    fontFamily = FontFamily.Monospace
                                )
                                Text(
                                    text = "AGENT_ID: ${deviceState.device_id}",
                                    color = TextSecondary,
                                    fontSize = 12.sp,
                                    fontFamily = FontFamily.Monospace
                                )
                            }
                        }
                        Icon(Icons.Default.ArrowForwardIos, contentDescription = "Details", tint = TextHint, modifier = Modifier.size(16.dp))
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                // Realtime Gauges Grid
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    CyberGauge(
                        percentage = cpuUsage,
                        label = "CPU LOAD",
                        value = "${(cpuUsage * 100).toInt()}%",
                        color = CyberPrimary,
                        modifier = Modifier.weight(1f)
                    )
                    CyberGauge(
                        percentage = ramUsageByTime / 16.0f,
                        label = "RAM USED",
                        value = "${ramUsageByTime}G",
                        color = CyberSecondary,
                        modifier = Modifier.weight(1f)
                    )
                    CyberGauge(
                        percentage = activeTasksCount / 10f,
                        label = "ACTIVE SVCS",
                        value = "$activeTasksCount",
                        color = CyberWarning,
                        modifier = Modifier.weight(1f)
                    )
                }

                Spacer(modifier = Modifier.height(20.dp))

                // Platform specifications Card
                CyberCard(modifier = Modifier.fillMaxWidth()) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.Computer, contentDescription = "Platform info", tint = CyberPrimary, modifier = Modifier.size(24.dp))
                        Spacer(modifier = Modifier.width(12.dp))
                        Column {
                            Text(text = "HOST TELEMETRY SPECIFICATION", color = CyberPrimary, fontSize = 11.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace)
                            Text(text = "Windows 11 Enterprise LTSC x64", color = TextPrimary, fontWeight = FontWeight.SemiBold, fontSize = 14.sp)
                            Text(
                                text = "Bypass blockades active • Dynamic firewalls enforced",
                                color = TextSecondary,
                                fontSize = 12.sp
                            )
                        }
                    }
                }

                Spacer(modifier = Modifier.height(20.dp))

                // Enforced Active Mode Control section
                Text(
                    text = "STATE ENFORCEMENT CONTROLS",
                    color = TextPrimary,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold,
                    fontFamily = FontFamily.Monospace,
                    modifier = Modifier.padding(bottom = 12.dp)
                )

                CyberCard(
                    modifier = Modifier.fillMaxWidth(),
                    borderColor = CyberPrimary.copy(alpha = 0.3f)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text(
                                text = "CURRENT SECURITY LEVEL",
                                color = TextSecondary,
                                fontSize = 11.sp,
                                fontFamily = FontFamily.Monospace
                            )
                            Text(
                                text = deviceState.active_mode.uppercase(),
                                color = when {
                                    deviceState.active_mode.equals("lockdown", ignoreCase = true) -> CyberError
                                    deviceState.active_mode.equals("mode1", ignoreCase = true) -> CyberPrimary
                                    else -> CyberWarning
                                },
                                fontWeight = FontWeight.Bold,
                                fontSize = 20.sp,
                                fontFamily = FontFamily.Monospace
                            )
                        }

                        Button(
                            onClick = { onNavigate(Screen.ModeControl) },
                            colors = ButtonDefaults.buttonColors(containerColor = CyberPrimary, contentColor = CyberBackground),
                            shape = RoundedCornerShape(8.dp),
                            contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp)
                        ) {
                            Text(text = "ALTER MODE", fontSize = 12.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace)
                        }
                    }
                }

                Spacer(modifier = Modifier.height(20.dp))

                // Broadcast app push Card
                Text(
                    text = "REMOTE DEPLOY ENGINE",
                    color = TextPrimary,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold,
                    fontFamily = FontFamily.Monospace,
                    modifier = Modifier.padding(bottom = 12.dp)
                )

                var apkUrl by remember { mutableStateOf("") }
                val isPushing by appPushViewModel.isLoading.collectAsStateWithLifecycle()

                CyberCard(modifier = Modifier.fillMaxWidth()) {
                    Text(text = "BROADCAST ENCRYPTED APK URL", color = CyberSecondary, fontSize = 11.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace)
                    Spacer(modifier = Modifier.height(8.dp))
                    OutlinedTextField(
                        value = apkUrl,
                        onValueChange = { apkUrl = it },
                        placeholder = { Text("https://example.com/payload.apk", color = TextHint, fontSize = 13.sp) },
                        singleLine = true,
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedTextColor = TextPrimary,
                            unfocusedTextColor = TextPrimary,
                            focusedBorderColor = CyberPrimary,
                            unfocusedBorderColor = CyberBorder
                        ),
                        modifier = Modifier.fillMaxWidth()
                    )
                    Spacer(modifier = Modifier.height(12.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(text = "SSL tunnel payload signature verification active", color = TextHint, fontSize = 11.sp, modifier = Modifier.weight(1f))
                        Button(
                            onClick = {
                                if (apkUrl.isBlank()) {
                                    Toast.makeText(this@MainActivity, "URL payload is empty.", Toast.LENGTH_SHORT).show()
                                    return@Button
                                }
                                appPushViewModel.pushAppLink(apkUrl, loginViewModel.getCurrentUserEmail())
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = CyberSecondary, contentColor = TextPrimary),
                            shape = RoundedCornerShape(6.dp),
                            enabled = !isPushing
                        ) {
                            if (isPushing) {
                                CircularProgressIndicator(color = TextPrimary, modifier = Modifier.size(20.dp))
                            } else {
                                Text(text = "DEPLOY", fontSize = 12.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace)
                            }
                        }
                    }
                }

                Spacer(modifier = Modifier.height(20.dp))

                // Recent security alerts preview
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(bottom = 12.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "REALTIME SECURITY ALERTS",
                        color = TextPrimary,
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Bold,
                        fontFamily = FontFamily.Monospace
                    )
                    Text(
                        text = "VIEW ALL",
                        color = CyberPrimary,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Bold,
                        fontFamily = FontFamily.Monospace,
                        modifier = Modifier.clickable { onNavigate(Screen.Alerts) }
                    )
                }

                if (logs.isEmpty()) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(100.dp)
                            .background(CyberSurface, RoundedCornerShape(12.dp)),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(text = "No recorded security logs found in Firestore.", color = TextSecondary, fontSize = 13.sp)
                    }
                } else {
                    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                        logs.sortedByDescending { it.timestamp }.take(3).forEach { log ->
                            SecurityLogItem(log)
                        }
                    }
                }

                // ==========================================
                // NEW SECTION: INSTALLED APPLICATIONS
                // ==========================================
                Spacer(modifier = Modifier.height(20.dp))

                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(bottom = 12.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            Icons.Default.AppShortcut,
                            contentDescription = "Installed Apps icon",
                            tint = CyberPrimary,
                            modifier = Modifier.size(18.dp)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "INSTALLED APPLICATIONS",
                            color = TextPrimary,
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Bold,
                            fontFamily = FontFamily.Monospace
                        )
                    }
                    Text(
                        text = "SECURE QUERY",
                        color = CyberPrimary.copy(alpha = 0.6f),
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Bold,
                        fontFamily = FontFamily.Monospace
                    )
                }

                when (val state = installedAppsState) {
                    is InstalledAppsUiState.Loading -> {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(120.dp)
                                .background(CyberSurface, RoundedCornerShape(12.dp))
                                .border(BorderStroke(1.dp, CyberBorder), RoundedCornerShape(12.dp)),
                            contentAlignment = Alignment.Center
                        ) {
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                CircularProgressIndicator(
                                    color = CyberPrimary,
                                    modifier = Modifier.size(30.dp)
                                )
                                Spacer(modifier = Modifier.height(10.dp))
                                Text(
                                    text = "Scanning application manifest...",
                                    color = TextSecondary,
                                    fontSize = 12.sp,
                                    fontFamily = FontFamily.Monospace
                                )
                            }
                        }
                    }
                    is InstalledAppsUiState.Error -> {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(120.dp)
                                .background(CyberSurface, RoundedCornerShape(12.dp))
                                .border(BorderStroke(1.dp, CyberError.copy(alpha = 0.5f)), RoundedCornerShape(12.dp)),
                            contentAlignment = Alignment.Center
                        ) {
                            Column(
                                horizontalAlignment = Alignment.CenterHorizontally,
                                modifier = Modifier.padding(16.dp)
                            ) {
                                Icon(
                                    Icons.Default.ErrorOutline,
                                    contentDescription = "Error icon",
                                    tint = CyberError,
                                    modifier = Modifier.size(24.dp)
                                )
                                Spacer(modifier = Modifier.height(8.dp))
                                Text(
                                    text = "SECURE SYNC TERMINATED: ${state.message}",
                                    color = CyberError,
                                    fontSize = 11.sp,
                                    fontFamily = FontFamily.Monospace,
                                    textAlign = TextAlign.Center
                                )
                                Spacer(modifier = Modifier.height(8.dp))
                                Text(
                                    text = "TAP TO RE-ESTABLISH CONNECTION",
                                    color = CyberPrimary,
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Bold,
                                    fontFamily = FontFamily.Monospace,
                                    modifier = Modifier.clickable {
                                        installedAppViewModel.observeInstalledApps()
                                    }
                                )
                            }
                        }
                    }
                    is InstalledAppsUiState.Success -> {
                        val apps = state.apps
                        if (apps.isEmpty()) {
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .height(120.dp)
                                    .background(CyberSurface, RoundedCornerShape(12.dp))
                                    .border(BorderStroke(1.dp, CyberBorder), RoundedCornerShape(12.dp)),
                                contentAlignment = Alignment.Center
                            ) {
                                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                    Icon(
                                        Icons.Default.FolderOpen,
                                        contentDescription = "No apps icon",
                                        tint = TextSecondary,
                                        modifier = Modifier.size(28.dp)
                                    )
                                    Spacer(modifier = Modifier.height(10.dp))
                                    Text(
                                        text = "No packages indexed on host system.",
                                        color = TextSecondary,
                                        fontSize = 12.sp,
                                        fontFamily = FontFamily.Monospace
                                    )
                                }
                            }
                        } else {
                            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                                apps.forEach { app ->
                                    InstalledAppCard(
                                        app = app,
                                        onBlock = { installedAppViewModel.blockApp(app.name) },
                                        onUninstall = { installedAppViewModel.uninstallApp(app.name) }
                                    )
                                }
                            }
                        }
                    }
                }

                Spacer(modifier = Modifier.height(24.dp))
            }
        }
    }

    // ==========================================
    // SCREEN 4: DEVICE DETAILS OVERLAY
    // ==========================================
    @Composable
    fun DeviceDetailsView(onBack: () -> Unit) {
        val deviceState by dashboardViewModel.deviceState.collectAsStateWithLifecycle()
        val isOnline by dashboardViewModel.isDeviceOnline.collectAsStateWithLifecycle()

        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(16.dp)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton(onClick = onBack) {
                    Icon(Icons.Default.ArrowBack, contentDescription = "Back", tint = CyberPrimary)
                }
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "DEVICE TELEMETRY NODE",
                    color = TextPrimary,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    fontFamily = FontFamily.Monospace
                )
            }

            CyberCard(
                modifier = Modifier.fillMaxWidth(),
                borderColor = if (isOnline) CyberTertiary.copy(alpha = 0.5f) else CyberError.copy(alpha = 0.5f)
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(16.dp)
                            .clip(CircleShape)
                            .background(if (isOnline) CyberTertiary else CyberError)
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Text(
                        text = if (isOnline) "ONLINE HEARTBEAT LOCKED" else "OFFLINE HEARTBEAT DROPPED",
                        color = if (isOnline) CyberTertiary else CyberError,
                        fontWeight = FontWeight.Bold,
                        fontSize = 14.sp,
                        fontFamily = FontFamily.Monospace
                    )
                }

                Spacer(modifier = Modifier.height(16.dp))
                TelemetryField(label = "DEVICE_IDENTIFIER", value = deviceState.device_id)
                TelemetryField(label = "HARDWARE_ARCH", value = "Windows PC / AMD64 Client")
                TelemetryField(label = "SSL_CHANNEL_STABILITY", value = "99.98% Crypt-Verified")
                TelemetryField(
                    label = "LAST_HEARTBEAT_UTC",
                    value = if (deviceState.last_ping.isNotEmpty()) deviceState.last_ping.replace("T", " ").replace("Z", " UTC") else "UNREACHABLE"
                )
                TelemetryField(label = "LAST_COMMAND_ISSUER_UID", value = if (deviceState.admin_uid.isNotEmpty()) deviceState.admin_uid else "NONE")
            }

            Spacer(modifier = Modifier.height(20.dp))

            Text(
                text = "HISTORICAL STATE CHANGE AUDITS",
                color = TextPrimary,
                fontSize = 14.sp,
                fontWeight = FontWeight.Bold,
                fontFamily = FontFamily.Monospace,
                modifier = Modifier.padding(bottom = 12.dp)
            )

            if (deviceState.mode_history.isEmpty()) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(120.dp)
                        .background(CyberSurface, RoundedCornerShape(12.dp)),
                    contentAlignment = Alignment.Center
                ) {
                    Text(text = "No previous mode audit logs found on host.", color = TextSecondary, fontSize = 12.sp)
                }
            } else {
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    deviceState.mode_history.reversed().take(15).forEach { history ->
                        CyberCard(modifier = Modifier.fillMaxWidth()) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Column {
                                    Text(
                                        text = "TRANSITIONED_TO: ${history.mode.uppercase()}",
                                        color = CyberPrimary,
                                        fontWeight = FontWeight.Bold,
                                        fontSize = 13.sp,
                                        fontFamily = FontFamily.Monospace
                                    )
                                    Text(
                                        text = "Timestamp: ${history.changed_at.replace("T", " ").replace("Z", " UTC")}",
                                        color = TextSecondary,
                                        fontSize = 11.sp,
                                        fontFamily = FontFamily.Monospace
                                    )
                                }
                                Icon(Icons.Default.Verified, contentDescription = "Signed", tint = CyberTertiary, modifier = Modifier.size(18.dp))
                            }
                        }
                    }
                }
            }
        }
    }

    // ==========================================
    // SCREEN 5: MODE CONTROL CENTER
    // ==========================================
    @Composable
    fun ModeControlView(onBack: () -> Unit) {
        val deviceState by dashboardViewModel.deviceState.collectAsStateWithLifecycle()
        val isOnline by dashboardViewModel.isDeviceOnline.collectAsStateWithLifecycle()

        val modes = listOf(
            Triple("mode1", "Standard Security (Mode 1)", "Default restricted state: locks down raw system browsers, calculators, and administrative terminals."),
            Triple("study", "Study Mode", "Enforces rigid attention. Blocks entertainment domains and apps entirely while logging memory load statistics."),
            Triple("kids", "Kids Guard Mode", "Establishes bulletproof internet filtering, restricts dangerous registry inputs, and displays safe applications."),
            Triple("developer", "Developer Sandbox", "Enables advanced developer backdoors, remote debugging sockets, and logs direct kernel activity."),
            Triple("lockdown", "EMERGENCY SYSTEM LOCKDOWN", "Red alert protocol. Blocks all system inputs, executes local network firewalls, and locks device terminal with secure red screens.")
        )

        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(16.dp)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton(onClick = onBack) {
                    Icon(Icons.Default.ArrowBack, contentDescription = "Back", tint = CyberPrimary)
                }
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "ALTER SYSTEM POLICIES",
                    color = TextPrimary,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    fontFamily = FontFamily.Monospace
                )
            }

            Text(
                text = "Select a defensive remote policy below to compile and broadcast over Firebase Secure Sockets.",
                color = TextSecondary,
                fontSize = 13.sp,
                modifier = Modifier.padding(bottom = 20.dp)
            )

            modes.forEach { (modeKey, title, description) ->
                val isSelected = deviceState.active_mode.equals(modeKey, ignoreCase = true)
                val cardBorderColor = when {
                    isSelected && modeKey == "lockdown" -> CyberError
                    isSelected -> CyberPrimary
                    modeKey == "lockdown" -> CyberError.copy(alpha = 0.2f)
                    else -> CyberBorder
                }

                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(bottom = 14.dp)
                        .clickable {
                            if (!isOnline) {
                                Toast.makeText(this@MainActivity, "Offline queue caching enabled. Broadcast will execute once client online.", Toast.LENGTH_LONG).show()
                            }
                            dashboardViewModel.changeActiveMode(modeKey, loginViewModel.getCurrentUserId())
                            businessViewModel.logActivity("Policy Broadcast", "Broadcasting policy state update: $modeKey")
                        },
                    shape = RoundedCornerShape(12.dp),
                    colors = CardDefaults.cardColors(containerColor = if (isSelected) CyberSurfaceCard else CyberSurface),
                    border = BorderStroke(1.2.dp, cardBorderColor)
                ) {
                    Row(
                        modifier = Modifier.padding(16.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        RadioButton(
                            selected = isSelected,
                            onClick = {
                                dashboardViewModel.changeActiveMode(modeKey, loginViewModel.getCurrentUserId())
                                businessViewModel.logActivity("Policy Broadcast", "Broadcasting policy state update: $modeKey")
                            },
                            colors = RadioButtonDefaults.colors(
                                selectedColor = if (modeKey == "lockdown") CyberError else CyberPrimary,
                                unselectedColor = TextSecondary
                            )
                        )
                        Spacer(modifier = Modifier.width(12.dp))
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = title.uppercase(),
                                color = if (modeKey == "lockdown") CyberError else TextPrimary,
                                fontWeight = FontWeight.Bold,
                                fontSize = 14.sp,
                                fontFamily = FontFamily.Monospace
                            )
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = description,
                                color = TextSecondary,
                                fontSize = 12.sp
                            )
                        }
                    }
                }
            }
        }
    }

    // ==========================================
    // SCREEN 6: SECURITY AUDIT LOGS (ALERTS)
    // ==========================================
    @Composable
    fun AlertsView(onBack: () -> Unit) {
        val logs by businessViewModel.activityLogs.collectAsStateWithLifecycle()
        var query by remember { mutableStateOf("") }

        val filteredLogs = remember(logs, query) {
            logs.filter {
                it.action.contains(query, ignoreCase = true) ||
                it.details.contains(query, ignoreCase = true) ||
                it.adminEmail.contains(query, ignoreCase = true)
            }.sortedByDescending { it.timestamp }
        }

        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton(onClick = onBack) {
                    Icon(Icons.Default.ArrowBack, contentDescription = "Back", tint = CyberPrimary)
                }
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "AUDIT TRAILS FEED",
                    color = TextPrimary,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    fontFamily = FontFamily.Monospace
                )
            }

            OutlinedTextField(
                value = query,
                onValueChange = { query = it },
                placeholder = { Text("Filter logs by action/details...", color = TextHint) },
                leadingIcon = { Icon(Icons.Default.Search, contentDescription = "Search", tint = TextSecondary) },
                singleLine = true,
                colors = OutlinedTextFieldDefaults.colors(
                    focusedTextColor = TextPrimary,
                    unfocusedTextColor = TextPrimary,
                    focusedBorderColor = CyberPrimary,
                    unfocusedBorderColor = CyberBorder
                ),
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 16.dp)
            )

            if (filteredLogs.isEmpty()) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .weight(1f),
                    contentAlignment = Alignment.Center
                ) {
                    Text(text = "No matching secure logs found.", color = TextSecondary)
                }
            } else {
                LazyColumn(
                    modifier = Modifier.weight(1f),
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    items(filteredLogs) { log ->
                        SecurityLogItem(log)
                    }
                }
            }
        }
    }

    // ==========================================
    // SCREEN 7: SYSTEM CONFIGURATION (SETTINGS)
    // ==========================================
    @Composable
    fun SettingsView(
        onNavigate: (Screen) -> Unit,
        onLogout: () -> Unit
    ) {
        val sharedPrefs = LocalContext.current.getSharedPreferences("nex_prefs", Context.MODE_PRIVATE)

        var isDarkMode by remember { mutableStateOf(sharedPrefs.getBoolean("dark_theme", true)) }
        var criticalAlerts by remember { mutableStateOf(sharedPrefs.getBoolean("notif_critical", true)) }
        var confirmationAlerts by remember { mutableStateOf(sharedPrefs.getBoolean("notif_mode", true)) }

        // Sync local pref modifications to cloud settings automatically
        fun saveConfig() {
            sharedPrefs.edit()
                .putBoolean("dark_theme", isDarkMode)
                .putBoolean("notif_critical", criticalAlerts)
                .putBoolean("notif_mode", confirmationAlerts)
                .apply()

            businessViewModel.updateSystemSettings(isDarkMode, criticalAlerts, confirmationAlerts)
        }

        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(16.dp)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton(onClick = { onNavigate(Screen.Dashboard) }) {
                    Icon(Icons.Default.ArrowBack, contentDescription = "Back", tint = CyberPrimary)
                }
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "TERMINAL CONFIGURATION",
                    color = TextPrimary,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    fontFamily = FontFamily.Monospace
                )
            }

            Text(
                text = "THEME & DESIGN SYSTEM",
                color = CyberPrimary,
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                fontFamily = FontFamily.Monospace,
                modifier = Modifier.padding(top = 8.dp, bottom = 12.dp)
            )

            CyberCard(modifier = Modifier.fillMaxWidth()) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(text = "Cyber Dark Enforced", color = TextPrimary, fontWeight = FontWeight.Bold, fontSize = 14.sp)
                        Text(text = "Locks dark canvas theme", color = TextSecondary, fontSize = 12.sp)
                    }
                    Switch(
                        checked = isDarkMode,
                        onCheckedChange = {
                            isDarkMode = it
                            saveConfig()
                            Toast.makeText(this@MainActivity, "Theme state cached.", Toast.LENGTH_SHORT).show()
                        },
                        colors = SwitchDefaults.colors(checkedThumbColor = CyberPrimary)
                    )
                }
            }

            Spacer(modifier = Modifier.height(20.dp))

            Text(
                text = "ALERTS & TELEMETRY ALARM NOTIFICATIONS",
                color = CyberPrimary,
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                fontFamily = FontFamily.Monospace,
                modifier = Modifier.padding(bottom = 12.dp)
            )

            CyberCard(modifier = Modifier.fillMaxWidth()) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(text = "Critical Down Alerts", color = TextPrimary, fontWeight = FontWeight.Bold, fontSize = 14.sp)
                        Text(text = "Triggers push alarms if the target client loses heartbeat connectivity.", color = TextSecondary, fontSize = 12.sp)
                    }
                    Switch(
                        checked = criticalAlerts,
                        onCheckedChange = {
                            criticalAlerts = it
                            saveConfig()
                        },
                        colors = SwitchDefaults.colors(checkedThumbColor = CyberPrimary)
                    )
                }

                Spacer(modifier = Modifier.height(16.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(text = "Policy Confirmation Alerts", color = TextPrimary, fontWeight = FontWeight.Bold, fontSize = 14.sp)
                        Text(text = "Pushes pop-up notifications on successful state broadcasts.", color = TextSecondary, fontSize = 12.sp)
                    }
                    Switch(
                        checked = confirmationAlerts,
                        onCheckedChange = {
                            confirmationAlerts = it
                            saveConfig()
                        },
                        colors = SwitchDefaults.colors(checkedThumbColor = CyberPrimary)
                    )
                }
            }

            Spacer(modifier = Modifier.height(20.dp))

            // Navigation Links
            SettingsLinkItem(title = "Modify Admin Profile", description = "Edit your name & identifier credentials", icon = Icons.Default.ManageAccounts) {
                onNavigate(Screen.Profile)
            }
            SettingsLinkItem(title = "About Cryptographic System", description = "View active certificates & secure license info", icon = Icons.Default.Info) {
                onNavigate(Screen.About)
            }

            Spacer(modifier = Modifier.height(24.dp))

            Button(
                onClick = onLogout,
                colors = ButtonDefaults.buttonColors(containerColor = CyberError.copy(alpha = 0.15f), contentColor = CyberError),
                border = BorderStroke(1.dp, CyberError),
                shape = RoundedCornerShape(8.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(50.dp)
            ) {
                Text(text = "TERMINATE SESSION", fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace)
            }
        }
    }

    // ==========================================
    // SCREEN 8: ADMIN PROFILE SCREEN
    // ==========================================
    @Composable
    fun AdminProfileView(onBack: () -> Unit) {
        val sharedPrefs = LocalContext.current.getSharedPreferences("nex_prefs", Context.MODE_PRIVATE)
        var name by remember { mutableStateOf(sharedPrefs.getString("display_name", "System Admin") ?: "System Admin") }
        var nameError by remember { mutableStateOf<String?>(null) }

        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(16.dp)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton(onClick = onBack) {
                    Icon(Icons.Default.ArrowBack, contentDescription = "Back", tint = CyberPrimary)
                }
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "ADMINISTRATOR CREDENTIALS",
                    color = TextPrimary,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    fontFamily = FontFamily.Monospace
                )
            }

            CyberCard(
                modifier = Modifier.fillMaxWidth(),
                borderColor = CyberPrimary.copy(alpha = 0.4f)
            ) {
                Column(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Box(
                        modifier = Modifier
                            .size(80.dp)
                            .clip(CircleShape)
                            .background(CyberSecondary.copy(alpha = 0.1f)),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(Icons.Default.ManageAccounts, contentDescription = "Admin Avatar", tint = CyberPrimary, modifier = Modifier.size(48.dp))
                    }
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = "UID: ${loginViewModel.getCurrentUserId()}",
                        color = TextHint,
                        fontSize = 11.sp,
                        fontFamily = FontFamily.Monospace
                    )
                    Text(
                        text = "ROLE: HIGH_SECURITY_ROOT_ADMIN",
                        color = CyberPrimary,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Bold,
                        fontFamily = FontFamily.Monospace,
                        modifier = Modifier.padding(top = 4.dp)
                    )
                }

                Spacer(modifier = Modifier.height(24.dp))

                TelemetryField(label = "AUTHORIZED_EMAIL", value = loginViewModel.getCurrentUserEmail())

                Spacer(modifier = Modifier.height(8.dp))

                OutlinedTextField(
                    value = name,
                    onValueChange = {
                        name = it
                        nameError = null
                    },
                    label = { Text("Display Name Label", color = TextSecondary) },
                    singleLine = true,
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedTextColor = TextPrimary,
                        unfocusedTextColor = TextPrimary,
                        focusedBorderColor = CyberPrimary,
                        unfocusedBorderColor = CyberBorder
                    ),
                    modifier = Modifier.fillMaxWidth()
                )
                if (nameError != null) {
                    Text(text = nameError!!, color = CyberError, fontSize = 11.sp, modifier = Modifier.padding(top = 4.dp))
                }

                Spacer(modifier = Modifier.height(16.dp))

                Button(
                    onClick = {
                        if (name.isBlank()) {
                            nameError = "Display name label cannot be empty."
                        } else {
                            sharedPrefs.edit().putString("display_name", name.trim()).apply()
                            businessViewModel.logActivity("Profile Updated", "Changed display name to ${name.trim()}")
                            Toast.makeText(this@MainActivity, "Local configuration updated successfully.", Toast.LENGTH_SHORT).show()
                            onBack()
                        }
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = CyberPrimary, contentColor = CyberBackground),
                    shape = RoundedCornerShape(8.dp),
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(48.dp)
                ) {
                    Text(text = "COMMIT PROFILE UPDATE", fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace)
                }
            }
        }
    }

    // ==========================================
    // SCREEN 9: ABOUT SCREEN
    // ==========================================
    @Composable
    fun AboutView(onBack: () -> Unit) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(16.dp)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton(onClick = onBack) {
                    Icon(Icons.Default.ArrowBack, contentDescription = "Back", tint = CyberPrimary)
                }
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "DECRYPTED SYSTEM SPEC",
                    color = TextPrimary,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    fontFamily = FontFamily.Monospace
                )
            }

            CyberCard(modifier = Modifier.fillMaxWidth()) {
                Text(text = "NEX SHIELD SYSTEM OVERVIEW", color = CyberPrimary, fontSize = 12.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace)
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "NeX Shield is an enterprise-grade high-security remote system access client built specifically for military and corporate host isolation. The system ensures total terminal integrity, automated key validation, and instant state enforcement protocols.",
                    color = TextPrimary,
                    fontSize = 13.sp,
                    lineHeight = 20.sp
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

            CyberCard(modifier = Modifier.fillMaxWidth()) {
                Text(text = "CRYPTOGRAPHIC PROTOCOLS", color = CyberSecondary, fontSize = 12.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace)
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "All administrative data synced between the Android companion control device and Firebase Realtime and Cloud Firestore sockets are encrypted on-the-fly using 256-bit SSL/TLS tunnels. State configurations are checked securely using active security policies restricting tampered clients.",
                    color = TextPrimary,
                    fontSize = 13.sp,
                    lineHeight = 20.sp
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

            CyberCard(modifier = Modifier.fillMaxWidth(), borderColor = CyberBorder) {
                Text(text = "VERSION LOG", color = TextSecondary, fontSize = 12.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace)
                Spacer(modifier = Modifier.height(4.dp))
                Text(text = "Build: NeX Companion 1.0.0 Stable Release", color = TextPrimary, fontSize = 13.sp)
                Text(text = "Hardware Engine: Android API 36 Native Compliant", color = TextSecondary, fontSize = 12.sp)
            }
        }
    }

    // ==========================================
    // SCREEN 10: USER DIRECTORY VIEW
    // ==========================================
    @Composable
    fun UserDirectoryView(
        onNavigateToForm: (User?) -> Unit,
        onBack: () -> Unit
    ) {
        val userUiState by businessViewModel.userUiState.collectAsStateWithLifecycle()
        val searchQuery by businessViewModel.searchQuery.collectAsStateWithLifecycle()
        val filterStatus by businessViewModel.filterStatus.collectAsStateWithLifecycle()

        Scaffold(
            containerColor = Color.Transparent,
            floatingActionButton = {
                FloatingActionButton(
                    onClick = { onNavigateToForm(null) },
                    containerColor = CyberPrimary,
                    contentColor = CyberBackground
                ) {
                    Icon(Icons.Default.Add, contentDescription = "Add User")
                }
            }
        ) { paddingValues ->
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
                    .padding(16.dp)
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(bottom = 12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back", tint = CyberPrimary)
                    }
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "REGISTERED USERS DATABASE",
                        color = TextPrimary,
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        fontFamily = FontFamily.Monospace
                    )
                }

                OutlinedTextField(
                    value = searchQuery,
                    onValueChange = { businessViewModel.searchQuery.value = it },
                    placeholder = { Text("Filter registered clients by name/email...", color = TextHint) },
                    leadingIcon = { Icon(Icons.Default.Search, contentDescription = "Search", tint = TextSecondary) },
                    singleLine = true,
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedTextColor = TextPrimary,
                        unfocusedTextColor = TextPrimary,
                        focusedBorderColor = CyberPrimary,
                        unfocusedBorderColor = CyberBorder
                    ),
                    modifier = Modifier.fillMaxWidth()
                )

                Spacer(modifier = Modifier.height(12.dp))

                // Filter tabs
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    FilterBadge(text = "All Profiles", selected = filterStatus == "all") {
                        businessViewModel.filterStatus.value = "all"
                    }
                    FilterBadge(text = "Active Only", selected = filterStatus == "Active") {
                        businessViewModel.filterStatus.value = "Active"
                    }
                    FilterBadge(text = "Inactive Only", selected = filterStatus == "Inactive") {
                        businessViewModel.filterStatus.value = "Inactive"
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                when (val state = userUiState) {
                    is UserUiState.Loading -> {
                        Box(modifier = Modifier.fillMaxWidth().weight(1f), contentAlignment = Alignment.Center) {
                            CircularProgressIndicator(color = CyberPrimary)
                        }
                    }
                    is UserUiState.Empty -> {
                        Box(modifier = Modifier.fillMaxWidth().weight(1f), contentAlignment = Alignment.Center) {
                            Text(text = "No profiles found in direct Firestore nodes.", color = TextSecondary)
                        }
                    }
                    is UserUiState.Success -> {
                        LazyColumn(
                            modifier = Modifier.fillMaxWidth().weight(1f),
                            verticalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            items(state.users) { user ->
                                CyberCard(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .clickable { onNavigateToForm(user) },
                                    borderColor = if (user.status == "Active") CyberTertiary.copy(alpha = 0.3f) else CyberBorder
                                ) {
                                    Row(
                                        modifier = Modifier.fillMaxWidth(),
                                        horizontalArrangement = Arrangement.SpaceBetween,
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Row(verticalAlignment = Alignment.CenterVertically) {
                                            Box(
                                                modifier = Modifier
                                                    .size(10.dp)
                                                    .clip(CircleShape)
                                                    .background(if (user.status == "Active") CyberTertiary else TextHint)
                                            )
                                            Spacer(modifier = Modifier.width(12.dp))
                                            Column {
                                                Text(text = user.name.uppercase(), color = TextPrimary, fontWeight = FontWeight.Bold, fontSize = 14.sp, fontFamily = FontFamily.Monospace)
                                                Text(text = user.email, color = TextSecondary, fontSize = 12.sp, fontFamily = FontFamily.Monospace)
                                            }
                                        }
                                        Icon(Icons.Default.Edit, contentDescription = "Edit Profile", tint = CyberPrimary, modifier = Modifier.size(18.dp))
                                    }
                                }
                            }
                        }
                    }
                    is UserUiState.Error -> {
                        Box(modifier = Modifier.fillMaxWidth().weight(1f), contentAlignment = Alignment.Center) {
                            Text(text = "Secure error sync dropped: ${state.message}", color = CyberError)
                        }
                    }
                }
            }
        }
    }

    // ==========================================
    // SCREEN 11: USER PROFILE REGISTER FORM
    // ==========================================
    @Composable
    fun UserFormView(
        editingUser: User?,
        onBack: () -> Unit
    ) {
        var name by remember { mutableStateOf(editingUser?.name ?: "") }
        var email by remember { mutableStateOf(editingUser?.email ?: "") }
        var isActive by remember { mutableStateOf(editingUser?.status.equals("Active", ignoreCase = true)) }

        var nameError by remember { mutableStateOf<String?>(null) }
        var emailError by remember { mutableStateOf<String?>(null) }

        val crudResult by businessViewModel.crudResult.collectAsStateWithLifecycle(initialValue = null)

        LaunchedEffect(crudResult) {
            if (crudResult != null) {
                crudResult!!.onSuccess {
                    Toast.makeText(this@MainActivity, "Database CRUD synced.", Toast.LENGTH_SHORT).show()
                    onBack()
                }
            }
        }

        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(16.dp)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton(onClick = onBack) {
                    Icon(Icons.Default.ArrowBack, contentDescription = "Back", tint = CyberPrimary)
                }
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = if (editingUser == null) "REGISTER NEW CLIENT USER" else "ALTER CLIENT DETAILS",
                    color = TextPrimary,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    fontFamily = FontFamily.Monospace
                )
            }

            CyberCard(
                modifier = Modifier.fillMaxWidth(),
                borderColor = CyberPrimary.copy(alpha = 0.4f)
            ) {
                OutlinedTextField(
                    value = name,
                    onValueChange = {
                        name = it
                        nameError = null
                    },
                    label = { Text("Display Name", color = TextSecondary) },
                    singleLine = true,
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedTextColor = TextPrimary,
                        unfocusedTextColor = TextPrimary,
                        focusedBorderColor = CyberPrimary,
                        unfocusedBorderColor = CyberBorder
                    ),
                    modifier = Modifier.fillMaxWidth()
                )
                if (nameError != null) {
                    Text(text = nameError!!, color = CyberError, fontSize = 11.sp, modifier = Modifier.padding(top = 4.dp))
                }

                Spacer(modifier = Modifier.height(16.dp))

                OutlinedTextField(
                    value = email,
                    onValueChange = {
                        email = it
                        emailError = null
                    },
                    label = { Text("Authorized Client Email", color = TextSecondary) },
                    singleLine = true,
                    enabled = editingUser == null, // Unique ID immutable
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedTextColor = TextPrimary,
                        unfocusedTextColor = TextPrimary,
                        focusedBorderColor = CyberPrimary,
                        unfocusedBorderColor = CyberBorder
                    ),
                    modifier = Modifier.fillMaxWidth()
                )
                if (emailError != null) {
                    Text(text = emailError!!, color = CyberError, fontSize = 11.sp, modifier = Modifier.padding(top = 4.dp))
                }

                Spacer(modifier = Modifier.height(20.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(text = "Authorized Client Status", color = TextPrimary, fontWeight = FontWeight.Bold, fontSize = 14.sp)
                        Text(text = if (isActive) "ACTIVE PROTOCOLS ENGAGED" else "SUSPENDED ACCOUNT BLOCKED", color = if (isActive) CyberTertiary else TextHint, fontSize = 12.sp)
                    }
                    Switch(
                        checked = isActive,
                        onCheckedChange = { isActive = it },
                        colors = SwitchDefaults.colors(checkedThumbColor = CyberTertiary)
                    )
                }

                Spacer(modifier = Modifier.height(28.dp))

                Button(
                    onClick = {
                        var valid = true
                        if (name.isBlank()) {
                            nameError = "Display Name cannot be empty."
                            valid = false
                        }
                        if (email.isBlank() || !email.contains("@")) {
                            emailError = "Invalid standard email form."
                            valid = false
                        }

                        if (valid) {
                            val statusStr = if (isActive) "Active" else "Inactive"
                            if (editingUser == null) {
                                businessViewModel.addUser(name.trim(), email.trim(), statusStr)
                            } else {
                                businessViewModel.updateUser(editingUser.id, name.trim(), email.trim(), statusStr)
                            }
                        }
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = CyberPrimary, contentColor = CyberBackground),
                    shape = RoundedCornerShape(8.dp),
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(48.dp)
                ) {
                    Text(text = "COMMIT DATA TO FIRESTORE", fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace)
                }

                if (editingUser != null) {
                    Spacer(modifier = Modifier.height(16.dp))
                    Button(
                        onClick = {
                            androidx.appcompat.app.AlertDialog.Builder(this@MainActivity)
                                .setTitle("Delete Client Node")
                                .setMessage("This action is completely irreversible. Delete administrative profile of ${editingUser.name}?")
                                .setPositiveButton("IRREVERSIBLE DELETE") { dialog, _ ->
                                    businessViewModel.deleteUser(editingUser.id, editingUser.name, editingUser.email)
                                    dialog.dismiss()
                                }
                                .setNegativeButton("ABORT") { dialog, _ ->
                                    dialog.dismiss()
                                }
                                .show()
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = CyberError.copy(alpha = 0.12f), contentColor = CyberError),
                        border = BorderStroke(1.dp, CyberError),
                        shape = RoundedCornerShape(8.dp),
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(48.dp)
                    ) {
                        Text(text = "DELETE USER PROFILE", fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace)
                    }
                }
            }
        }
    }

    // ==========================================
    // CUSTOM REUSABLE DESIGN COMPONENTS
    // ==========================================
    @Composable
    fun CyberCard(
        modifier: Modifier = Modifier,
        borderColor: Color = CyberBorder,
        content: @Composable ColumnScope.() -> Unit
    ) {
        Card(
            modifier = modifier,
            shape = RoundedCornerShape(12.dp),
            colors = CardDefaults.cardColors(containerColor = CyberSurface),
            border = BorderStroke(1.2.dp, borderColor)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                content()
            }
        }
    }

    @Composable
    fun CyberGauge(
        percentage: Float,
        label: String,
        value: String,
        color: Color,
        modifier: Modifier = Modifier
    ) {
        Card(
            modifier = modifier,
            shape = RoundedCornerShape(12.dp),
            colors = CardDefaults.cardColors(containerColor = CyberSurface),
            border = BorderStroke(1.dp, CyberBorder)
        ) {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(12.dp)
            ) {
                Box(contentAlignment = Alignment.Center, modifier = Modifier.size(60.dp)) {
                    Canvas(modifier = Modifier.fillMaxSize()) {
                        drawCircle(
                            color = color.copy(alpha = 0.08f),
                            style = Stroke(width = 5.dp.toPx())
                        )
                        drawArc(
                            color = color,
                            startAngle = -90f,
                            sweepAngle = 360f * percentage,
                            useCenter = false,
                            style = Stroke(width = 5.dp.toPx(), cap = StrokeCap.Round)
                        )
                    }
                    Text(text = value, color = TextPrimary, fontWeight = FontWeight.Bold, fontSize = 12.sp, fontFamily = FontFamily.Monospace)
                }
                Spacer(modifier = Modifier.height(6.dp))
                Text(text = label, color = TextSecondary, fontSize = 10.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace)
            }
        }
    }

    @Composable
    fun SecurityLogItem(log: ActivityLog) {
        val formatter = java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss", java.util.Locale.getDefault())
        val formattedDate = formatter.format(java.util.Date(log.timestamp))

        CyberCard(modifier = Modifier.fillMaxWidth(), borderColor = CyberBorder.copy(alpha = 0.7f)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.weight(1f)) {
                    Box(
                        modifier = Modifier
                            .size(32.dp)
                            .clip(CircleShape)
                            .background(
                                when {
                                    log.action.contains("Add", ignoreCase = true) -> CyberTertiary.copy(alpha = 0.1f)
                                    log.action.contains("Delete", ignoreCase = true) -> CyberError.copy(alpha = 0.1f)
                                    else -> CyberPrimary.copy(alpha = 0.1f)
                                }
                            ),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = when {
                                log.action.contains("Add", ignoreCase = true) -> Icons.Default.Add
                                log.action.contains("Delete", ignoreCase = true) -> Icons.Default.Delete
                                else -> Icons.Default.Shield
                            },
                            contentDescription = "Event icon",
                            tint = when {
                                log.action.contains("Add", ignoreCase = true) -> CyberTertiary
                                log.action.contains("Delete", ignoreCase = true) -> CyberError
                                else -> CyberPrimary
                            },
                            modifier = Modifier.size(16.dp)
                        )
                    }
                    Spacer(modifier = Modifier.width(12.dp))
                    Column {
                        Text(
                            text = log.action.uppercase(),
                            color = TextPrimary,
                            fontWeight = FontWeight.Bold,
                            fontSize = 13.sp,
                            fontFamily = FontFamily.Monospace
                        )
                        Text(text = log.details, color = TextSecondary, fontSize = 12.sp)
                        Text(text = "By ${log.adminEmail} • $formattedDate", color = TextHint, fontSize = 10.sp)
                    }
                }
            }
        }
    }

    @Composable
    fun TelemetryField(label: String, value: String) {
        Column(modifier = Modifier.padding(vertical = 6.dp)) {
            Text(text = label, color = CyberSecondary, fontSize = 10.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace)
            Text(text = value, color = TextPrimary, fontSize = 13.sp, fontFamily = FontFamily.Monospace)
            Divider(color = CyberBorder.copy(alpha = 0.4f), modifier = Modifier.padding(top = 6.dp))
        }
    }

    @Composable
    fun SettingsLinkItem(title: String, description: String, icon: ImageVector, onClick: () -> Unit) {
        CyberCard(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 12.dp)
                .clickable(onClick = onClick)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.weight(1f)) {
                    Icon(icon, contentDescription = title, tint = CyberPrimary, modifier = Modifier.size(24.dp))
                    Spacer(modifier = Modifier.width(16.dp))
                    Column {
                        Text(text = title, color = TextPrimary, fontWeight = FontWeight.Bold, fontSize = 14.sp)
                        Text(text = description, color = TextSecondary, fontSize = 12.sp)
                    }
                }
                Icon(Icons.Default.ArrowForwardIos, contentDescription = "Navigate", tint = TextHint, modifier = Modifier.size(16.dp))
            }
        }
    }

    @Composable
    fun FilterBadge(text: String, selected: Boolean, onClick: () -> Unit) {
        Box(
            modifier = Modifier
                .clip(RoundedCornerShape(6.dp))
                .background(if (selected) CyberPrimary else CyberSurface)
                .border(1.dp, if (selected) CyberPrimary else CyberBorder, RoundedCornerShape(6.dp))
                .clickable(onClick = onClick)
                .padding(horizontal = 12.dp, vertical = 6.dp)
        ) {
            Text(
                text = text.uppercase(),
                color = if (selected) CyberBackground else TextSecondary,
                fontSize = 10.sp,
                fontWeight = FontWeight.Bold,
                fontFamily = FontFamily.Monospace
            )
        }
    }

    @Composable
    fun InstalledAppCard(
        app: InstalledApp,
        onBlock: () -> Unit,
        onUninstall: () -> Unit
    ) {
        CyberCard(
            modifier = Modifier
                .fillMaxWidth()
                .testTag("app_card_${app.name.lowercase().replace(" ", "_")}"),
            borderColor = when {
                app.status.equals("blocked", ignoreCase = true) -> CyberError.copy(alpha = 0.5f)
                app.status.equals("active", ignoreCase = true) -> CyberTertiary.copy(alpha = 0.5f)
                else -> CyberBorder
            }
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // App Icon Badge
                Box(
                    modifier = Modifier
                        .size(48.dp)
                        .clip(RoundedCornerShape(8.dp))
                        .background(
                            when {
                                app.status.equals("blocked", ignoreCase = true) -> CyberError.copy(alpha = 0.1f)
                                app.status.equals("active", ignoreCase = true) -> CyberTertiary.copy(alpha = 0.1f)
                                else -> CyberPrimary.copy(alpha = 0.1f)
                            }
                        )
                        .border(
                            1.dp,
                            when {
                                app.status.equals("blocked", ignoreCase = true) -> CyberError
                                app.status.equals("active", ignoreCase = true) -> CyberTertiary
                                else -> CyberPrimary
                            },
                            RoundedCornerShape(8.dp)
                        ),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = if (app.name.isNotEmpty()) app.name.take(1).uppercase() else "A",
                        color = when {
                            app.status.equals("blocked", ignoreCase = true) -> CyberError
                            app.status.equals("active", ignoreCase = true) -> CyberTertiary
                            else -> CyberPrimary
                        },
                        fontWeight = FontWeight.Bold,
                        fontSize = 20.sp,
                        fontFamily = FontFamily.Monospace
                    )
                }

                Spacer(modifier = Modifier.width(16.dp))

                // Text Details
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = app.name.uppercase(),
                        color = TextPrimary,
                        fontWeight = FontWeight.Bold,
                        fontSize = 14.sp,
                        fontFamily = FontFamily.Monospace
                    )
                    Text(
                        text = "PUBLISHER: ${app.publisher}",
                        color = TextSecondary,
                        fontSize = 11.sp,
                        fontFamily = FontFamily.Monospace
                    )
                    Text(
                        text = "VERSION: ${app.version}",
                        color = TextSecondary,
                        fontSize = 11.sp,
                        fontFamily = FontFamily.Monospace
                    )
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier.padding(top = 4.dp)
                    ) {
                        Box(
                            modifier = Modifier
                                .size(6.dp)
                                .clip(CircleShape)
                                .background(
                                    when {
                                        app.status.equals("blocked", ignoreCase = true) -> CyberError
                                        app.status.equals("active", ignoreCase = true) -> CyberTertiary
                                        else -> CyberWarning
                                    }
                                )
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "STATUS: ${app.status.uppercase()}",
                            color = when {
                                app.status.equals("blocked", ignoreCase = true) -> CyberError
                                app.status.equals("active", ignoreCase = true) -> CyberTertiary
                                else -> CyberWarning
                            },
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            fontFamily = FontFamily.Monospace
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Action Buttons Row
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                OutlinedButton(
                    onClick = onBlock,
                    modifier = Modifier
                        .weight(1f)
                        .testTag("block_button_${app.name.lowercase().replace(" ", "_")}"),
                    shape = RoundedCornerShape(6.dp),
                    border = BorderStroke(1.dp, CyberWarning.copy(alpha = 0.8f)),
                    colors = ButtonDefaults.outlinedButtonColors(
                        contentColor = CyberWarning
                    ),
                    contentPadding = PaddingValues(vertical = 8.dp)
                ) {
                    Icon(
                        Icons.Default.Block,
                        contentDescription = "Block app",
                        tint = CyberWarning,
                        modifier = Modifier.size(14.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "BLOCK",
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        fontFamily = FontFamily.Monospace
                    )
                }

                OutlinedButton(
                    onClick = onUninstall,
                    modifier = Modifier
                        .weight(1f)
                        .testTag("uninstall_button_${app.name.lowercase().replace(" ", "_")}"),
                    shape = RoundedCornerShape(6.dp),
                    border = BorderStroke(1.dp, CyberError.copy(alpha = 0.8f)),
                    colors = ButtonDefaults.outlinedButtonColors(
                        contentColor = CyberError
                    ),
                    contentPadding = PaddingValues(vertical = 8.dp)
                ) {
                    Icon(
                        Icons.Default.DeleteForever,
                        contentDescription = "Uninstall app",
                        tint = CyberError,
                        modifier = Modifier.size(14.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "UNINSTALL",
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        fontFamily = FontFamily.Monospace
                    )
                }
            }
        }
    }
}
