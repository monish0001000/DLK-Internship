package com.example.ui.theme

import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalContext

private val DarkColorScheme = darkColorScheme(
    primary = CyberPrimary,
    onPrimary = CyberBackground,
    secondary = CyberSecondary,
    onSecondary = TextPrimary,
    tertiary = CyberTertiary,
    onTertiary = CyberBackground,
    background = CyberBackground,
    onBackground = TextPrimary,
    surface = CyberSurface,
    onSurface = TextPrimary,
    error = CyberError,
    onError = TextPrimary,
    surfaceVariant = CyberSurfaceCard,
    onSurfaceVariant = TextSecondary,
    outline = CyberBorder
)

private val LightColorScheme = darkColorScheme( // Enforce a cool technical dark/slate scheme for light mode too, or slate blue
    primary = CyberPrimary,
    onPrimary = CyberBackground,
    secondary = CyberSecondary,
    onSecondary = TextPrimary,
    tertiary = CyberTertiary,
    onTertiary = CyberBackground,
    background = CyberBackground,
    onBackground = TextPrimary,
    surface = CyberSurface,
    onSurface = TextPrimary,
    error = CyberError,
    onError = TextPrimary,
    surfaceVariant = CyberSurfaceCard,
    onSurfaceVariant = TextSecondary,
    outline = CyberBorder
)

@Composable
fun MyApplicationTheme(
  darkTheme: Boolean = isSystemInDarkTheme(),
  // Dynamic color is available on Android 12+
  dynamicColor: Boolean = true,
  content: @Composable () -> Unit,
) {
  val colorScheme =
    when {
      dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
        val context = LocalContext.current
        if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
      }

      darkTheme -> DarkColorScheme
      else -> LightColorScheme
    }

  MaterialTheme(colorScheme = colorScheme, typography = Typography, content = content)
}
