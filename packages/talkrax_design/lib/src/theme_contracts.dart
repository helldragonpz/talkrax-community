// Copyright (c) 2026 Alexandar Penev.
// SPDX-License-Identifier: AGPL-3.0-only

import 'package:flutter/material.dart';

class TalkraxAccentTheme {
  const TalkraxAccentTheme({
    required this.id,
    required this.name,
    required this.primary,
    required this.secondary,
    required this.accent,
  });

  final String id;
  final String name;
  final Color primary;
  final Color secondary;
  final Color accent;
}

class TalkraxVisualThemePack {
  const TalkraxVisualThemePack({
    required this.id,
    this.slug = '',
    required this.name,
    required this.description,
    this.source = 'official',
    this.tier = 'free',
    this.previewImageAssetId = '',
    this.previewGalleryAssetIds = const [],
    this.heroBackgroundAssetId,
    this.appBackgroundAssetId,
    this.spaceHeaderBackgroundAssetId,
    this.profileBackgroundAssetId,
    this.animatedBackgroundAssetId,
    this.themeManifestJson = const {},
    this.priceCents = 0,
    this.currency = 'EUR',
    this.createdAt = '2026-06-07T00:00:00Z',
    this.updatedAt = '2026-06-07T00:00:00Z',
    this.status = 'active',
    required this.cardRadius,
    required this.controlRadius,
    required this.glowColor,
    required this.motionDuration,
    required this.panelOpacity,
    required this.backgroundImageOpacity,
    required this.backgroundImageAsset,
    required this.backgroundGradient,
    required this.isPremium,
    required this.priceEur,
    this.staticBackgrounds = const {},
    this.overlayEffect = 'none',
    this.roomListStyle = 'standard',
    this.memberListStyle = 'standard',
    this.messageStyle = 'compact-modern',
    this.profileStyle = 'clean',
    this.badgeStyle = 'standard',
    this.iconStyle = 'standard',
    this.controlSurfaceAssetId,
    this.controlSurfaceHoverAssetId,
    this.outlinedControlSurfaceAssetId,
    this.iconSurfaceAssetId,
    this.panelSurfaceAssetId,
    this.sidebarSurfaceAssetId,
    this.navRailSurfaceAssetId,
    this.messageSurfaceAssetId,
    this.dividerSurfaceAssetId,
    this.streamFrameSurfaceAssetId,
    this.mobileFallbackAssetId,
    this.reducedMotionFallbackAssetId,
    this.lowPowerFallbackAssetId,
  });

  final String id;
  final String slug;
  final String name;
  final String description;
  final String source;
  final String tier;
  final String previewImageAssetId;
  final List<String> previewGalleryAssetIds;
  final String? heroBackgroundAssetId;
  final String? appBackgroundAssetId;
  final String? spaceHeaderBackgroundAssetId;
  final String? profileBackgroundAssetId;
  final String? animatedBackgroundAssetId;
  final Map<String, Object?> themeManifestJson;
  final int priceCents;
  final String currency;
  final String createdAt;
  final String updatedAt;
  final String status;
  final double cardRadius;
  final double controlRadius;
  final Color glowColor;
  final int motionDuration;
  final double panelOpacity;
  final double backgroundImageOpacity;
  final String? backgroundImageAsset;
  final List<Color>? backgroundGradient;
  final bool isPremium;
  final double? priceEur;
  final Map<String, String> staticBackgrounds;
  final String overlayEffect;
  final String roomListStyle;
  final String memberListStyle;
  final String messageStyle;
  final String profileStyle;
  final String badgeStyle;
  final String iconStyle;
  final String? controlSurfaceAssetId;
  final String? controlSurfaceHoverAssetId;
  final String? outlinedControlSurfaceAssetId;
  final String? iconSurfaceAssetId;
  final String? panelSurfaceAssetId;
  final String? sidebarSurfaceAssetId;
  final String? navRailSurfaceAssetId;
  final String? messageSurfaceAssetId;
  final String? dividerSurfaceAssetId;
  final String? streamFrameSurfaceAssetId;
  final String? mobileFallbackAssetId;
  final String? reducedMotionFallbackAssetId;
  final String? lowPowerFallbackAssetId;

  String get packageSlug => slug.isEmpty ? id : slug;

  String get priceLabel => priceCents <= 0
      ? 'Included'
      : '${(priceCents / 100).toStringAsFixed(2)} $currency';

  bool get hasAnimatedBackground =>
      animatedBackgroundAssetId != null || overlayEffect != 'none';

  String? backgroundForVariant(String variant) {
    final normalized = variant.trim().toLowerCase();
    return staticBackgrounds[normalized] ??
        staticBackgrounds['default'] ??
        appBackgroundAssetId ??
        backgroundImageAsset;
  }
}

@immutable
class TalkraxVisualThemeToken extends ThemeExtension<TalkraxVisualThemeToken> {
  const TalkraxVisualThemeToken({
    this.imageProviderFactory,
    required this.packId,
    required this.backgroundGradient,
    required this.backgroundImageAsset,
    required this.backgroundImageOpacity,
    required this.controlRadius,
    required this.motionDuration,
    required this.glowColor,
    required this.overlayEffect,
    required this.animatedBackgroundEnabled,
    required this.lowPowerThemeMode,
    required this.reducedMotion,
    required this.heroBackgroundAsset,
    required this.profileBackgroundAsset,
    required this.mobileFallbackAsset,
    required this.reducedMotionFallbackAsset,
    required this.lowPowerFallbackAsset,
    required this.roomListStyle,
    required this.memberListStyle,
    required this.messageStyle,
    required this.messageMentionBackground,
    required this.messageMentionBorder,
    required this.messageReplyBackground,
    required this.messageReplyBorder,
    required this.unreadMentionGlow,
    required this.unreadReplyGlow,
    required this.profileStyle,
    required this.badgeStyle,
    required this.iconStyle,
    required this.controlSurfaceAsset,
    required this.controlSurfaceHoverAsset,
    required this.outlinedControlSurfaceAsset,
    required this.iconSurfaceAsset,
    required this.panelSurfaceAsset,
    required this.sidebarSurfaceAsset,
    required this.navRailSurfaceAsset,
    required this.messageSurfaceAsset,
    required this.dividerSurfaceAsset,
    required this.streamFrameSurfaceAsset,
  });

  final ImageProvider<Object> Function(String)? imageProviderFactory;
  final String packId;
  final List<Color>? backgroundGradient;
  final String? backgroundImageAsset;
  final double backgroundImageOpacity;
  final double controlRadius;
  final Duration motionDuration;
  final Color glowColor;
  final String overlayEffect;
  final bool animatedBackgroundEnabled;
  final bool lowPowerThemeMode;
  final bool reducedMotion;
  final String? heroBackgroundAsset;
  final String? profileBackgroundAsset;
  final String? mobileFallbackAsset;
  final String? reducedMotionFallbackAsset;
  final String? lowPowerFallbackAsset;
  final String roomListStyle;
  final String memberListStyle;
  final String messageStyle;
  final Color messageMentionBackground;
  final Color messageMentionBorder;
  final Color messageReplyBackground;
  final Color messageReplyBorder;
  final Color unreadMentionGlow;
  final Color unreadReplyGlow;
  final String profileStyle;
  final String badgeStyle;
  final String iconStyle;
  final String? controlSurfaceAsset;
  final String? controlSurfaceHoverAsset;
  final String? outlinedControlSurfaceAsset;
  final String? iconSurfaceAsset;
  final String? panelSurfaceAsset;
  final String? sidebarSurfaceAsset;
  final String? navRailSurfaceAsset;
  final String? messageSurfaceAsset;
  final String? dividerSurfaceAsset;
  final String? streamFrameSurfaceAsset;

  bool get allowsAnimatedEffects =>
      animatedBackgroundEnabled && !lowPowerThemeMode && !reducedMotion;

  String? effectiveBackgroundAsset(BuildContext context) {
    final compact = MediaQuery.sizeOf(context).shortestSide < 600;
    // A portrait/mobile crop is a layout requirement, so keep it even when
    // animation is disabled or the low-power preference is active.
    if (compact && mobileFallbackAsset != null) return mobileFallbackAsset;
    if (lowPowerThemeMode && lowPowerFallbackAsset != null) {
      return lowPowerFallbackAsset;
    }
    if ((reducedMotion ||
            (MediaQuery.maybeOf(context)?.disableAnimations ?? false)) &&
        reducedMotionFallbackAsset != null) {
      return reducedMotionFallbackAsset;
    }
    return backgroundImageAsset;
  }

  String? effectiveProfileBackgroundAsset(BuildContext context) {
    if (lowPowerThemeMode && lowPowerFallbackAsset != null) {
      return lowPowerFallbackAsset;
    }
    if ((reducedMotion ||
            (MediaQuery.maybeOf(context)?.disableAnimations ?? false)) &&
        reducedMotionFallbackAsset != null) {
      return reducedMotionFallbackAsset;
    }
    return profileBackgroundAsset ?? effectiveBackgroundAsset(context);
  }

  String? effectiveHeroBackgroundAsset(BuildContext context) {
    if (lowPowerThemeMode && lowPowerFallbackAsset != null) {
      return lowPowerFallbackAsset;
    }
    if ((reducedMotion ||
            (MediaQuery.maybeOf(context)?.disableAnimations ?? false)) &&
        reducedMotionFallbackAsset != null) {
      return reducedMotionFallbackAsset;
    }
    return heroBackgroundAsset ?? effectiveBackgroundAsset(context);
  }

  BoxDecoration backgroundDecoration(
    ColorScheme colorScheme, {
    String? imageAsset,
  }) {
    final gradient = backgroundGradient == null || backgroundGradient!.isEmpty
        ? null
        : LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: backgroundGradient!,
          );
    final asset = imageAsset ?? backgroundImageAsset;
    final image = asset == null
        ? null
        : DecorationImage(
            image: imageProviderFactory?.call(asset) ?? AssetImage(asset),
            fit: BoxFit.cover,
            opacity: backgroundImageOpacity,
            colorFilter: ColorFilter.mode(
              colorScheme.surface.withValues(alpha: 0.6),
              BlendMode.multiply,
            ),
          );
    return BoxDecoration(
      color: colorScheme.surface,
      gradient: gradient,
      image: image,
    );
  }

  @override
  TalkraxVisualThemeToken copyWith({
    String? packId,
    List<Color>? backgroundGradient,
    String? backgroundImageAsset,
    double? backgroundImageOpacity,
    double? controlRadius,
    Duration? motionDuration,
    Color? glowColor,
    String? overlayEffect,
    bool? animatedBackgroundEnabled,
    bool? lowPowerThemeMode,
    bool? reducedMotion,
    String? heroBackgroundAsset,
    String? profileBackgroundAsset,
    String? mobileFallbackAsset,
    String? reducedMotionFallbackAsset,
    String? lowPowerFallbackAsset,
    String? roomListStyle,
    String? memberListStyle,
    String? messageStyle,
    Color? messageMentionBackground,
    Color? messageMentionBorder,
    Color? messageReplyBackground,
    Color? messageReplyBorder,
    Color? unreadMentionGlow,
    Color? unreadReplyGlow,
    String? profileStyle,
    String? badgeStyle,
    String? iconStyle,
    String? controlSurfaceAsset,
    String? controlSurfaceHoverAsset,
    String? outlinedControlSurfaceAsset,
    String? iconSurfaceAsset,
    String? panelSurfaceAsset,
    String? sidebarSurfaceAsset,
    String? navRailSurfaceAsset,
    String? messageSurfaceAsset,
    String? dividerSurfaceAsset,
    String? streamFrameSurfaceAsset,
  }) => TalkraxVisualThemeToken(
    imageProviderFactory: imageProviderFactory,
    packId: packId ?? this.packId,
    backgroundGradient: backgroundGradient ?? this.backgroundGradient,
    backgroundImageAsset: backgroundImageAsset ?? this.backgroundImageAsset,
    backgroundImageOpacity:
        backgroundImageOpacity ?? this.backgroundImageOpacity,
    controlRadius: controlRadius ?? this.controlRadius,
    motionDuration: motionDuration ?? this.motionDuration,
    glowColor: glowColor ?? this.glowColor,
    overlayEffect: overlayEffect ?? this.overlayEffect,
    animatedBackgroundEnabled:
        animatedBackgroundEnabled ?? this.animatedBackgroundEnabled,
    lowPowerThemeMode: lowPowerThemeMode ?? this.lowPowerThemeMode,
    reducedMotion: reducedMotion ?? this.reducedMotion,
    heroBackgroundAsset: heroBackgroundAsset ?? this.heroBackgroundAsset,
    profileBackgroundAsset:
        profileBackgroundAsset ?? this.profileBackgroundAsset,
    mobileFallbackAsset: mobileFallbackAsset ?? this.mobileFallbackAsset,
    reducedMotionFallbackAsset:
        reducedMotionFallbackAsset ?? this.reducedMotionFallbackAsset,
    lowPowerFallbackAsset: lowPowerFallbackAsset ?? this.lowPowerFallbackAsset,
    roomListStyle: roomListStyle ?? this.roomListStyle,
    memberListStyle: memberListStyle ?? this.memberListStyle,
    messageStyle: messageStyle ?? this.messageStyle,
    messageMentionBackground:
        messageMentionBackground ?? this.messageMentionBackground,
    messageMentionBorder: messageMentionBorder ?? this.messageMentionBorder,
    messageReplyBackground:
        messageReplyBackground ?? this.messageReplyBackground,
    messageReplyBorder: messageReplyBorder ?? this.messageReplyBorder,
    unreadMentionGlow: unreadMentionGlow ?? this.unreadMentionGlow,
    unreadReplyGlow: unreadReplyGlow ?? this.unreadReplyGlow,
    profileStyle: profileStyle ?? this.profileStyle,
    badgeStyle: badgeStyle ?? this.badgeStyle,
    iconStyle: iconStyle ?? this.iconStyle,
    controlSurfaceAsset: controlSurfaceAsset ?? this.controlSurfaceAsset,
    controlSurfaceHoverAsset:
        controlSurfaceHoverAsset ?? this.controlSurfaceHoverAsset,
    outlinedControlSurfaceAsset:
        outlinedControlSurfaceAsset ?? this.outlinedControlSurfaceAsset,
    iconSurfaceAsset: iconSurfaceAsset ?? this.iconSurfaceAsset,
    panelSurfaceAsset: panelSurfaceAsset ?? this.panelSurfaceAsset,
    sidebarSurfaceAsset: sidebarSurfaceAsset ?? this.sidebarSurfaceAsset,
    navRailSurfaceAsset: navRailSurfaceAsset ?? this.navRailSurfaceAsset,
    messageSurfaceAsset: messageSurfaceAsset ?? this.messageSurfaceAsset,
    dividerSurfaceAsset: dividerSurfaceAsset ?? this.dividerSurfaceAsset,
    streamFrameSurfaceAsset:
        streamFrameSurfaceAsset ?? this.streamFrameSurfaceAsset,
  );

  @override
  TalkraxVisualThemeToken lerp(
    ThemeExtension<TalkraxVisualThemeToken>? other,
    double t,
  ) {
    if (other is! TalkraxVisualThemeToken) return this;
    return TalkraxVisualThemeToken(
      imageProviderFactory: t < 0.5
          ? imageProviderFactory
          : other.imageProviderFactory,
      packId: t < 0.5 ? packId : other.packId,
      backgroundGradient: other.backgroundGradient ?? backgroundGradient,
      backgroundImageAsset: other.backgroundImageAsset ?? backgroundImageAsset,
      backgroundImageOpacity:
          backgroundImageOpacity +
          (other.backgroundImageOpacity - backgroundImageOpacity) * t,
      controlRadius: controlRadius + (other.controlRadius - controlRadius) * t,
      glowColor: Color.lerp(glowColor, other.glowColor, t) ?? glowColor,
      motionDuration: Duration(
        milliseconds:
            (motionDuration.inMilliseconds +
                    (other.motionDuration.inMilliseconds -
                            motionDuration.inMilliseconds) *
                        t)
                .round(),
      ),
      overlayEffect: t < 0.5 ? overlayEffect : other.overlayEffect,
      animatedBackgroundEnabled: t < 0.5
          ? animatedBackgroundEnabled
          : other.animatedBackgroundEnabled,
      lowPowerThemeMode: t < 0.5 ? lowPowerThemeMode : other.lowPowerThemeMode,
      reducedMotion: t < 0.5 ? reducedMotion : other.reducedMotion,
      heroBackgroundAsset: t < 0.5
          ? heroBackgroundAsset
          : other.heroBackgroundAsset,
      profileBackgroundAsset: t < 0.5
          ? profileBackgroundAsset
          : other.profileBackgroundAsset,
      mobileFallbackAsset: t < 0.5
          ? mobileFallbackAsset
          : other.mobileFallbackAsset,
      reducedMotionFallbackAsset: t < 0.5
          ? reducedMotionFallbackAsset
          : other.reducedMotionFallbackAsset,
      lowPowerFallbackAsset: t < 0.5
          ? lowPowerFallbackAsset
          : other.lowPowerFallbackAsset,
      roomListStyle: t < 0.5 ? roomListStyle : other.roomListStyle,
      memberListStyle: t < 0.5 ? memberListStyle : other.memberListStyle,
      messageStyle: t < 0.5 ? messageStyle : other.messageStyle,
      messageMentionBackground:
          Color.lerp(
            messageMentionBackground,
            other.messageMentionBackground,
            t,
          ) ??
          messageMentionBackground,
      messageMentionBorder:
          Color.lerp(messageMentionBorder, other.messageMentionBorder, t) ??
          messageMentionBorder,
      messageReplyBackground:
          Color.lerp(messageReplyBackground, other.messageReplyBackground, t) ??
          messageReplyBackground,
      messageReplyBorder:
          Color.lerp(messageReplyBorder, other.messageReplyBorder, t) ??
          messageReplyBorder,
      unreadMentionGlow:
          Color.lerp(unreadMentionGlow, other.unreadMentionGlow, t) ??
          unreadMentionGlow,
      unreadReplyGlow:
          Color.lerp(unreadReplyGlow, other.unreadReplyGlow, t) ??
          unreadReplyGlow,
      profileStyle: t < 0.5 ? profileStyle : other.profileStyle,
      badgeStyle: t < 0.5 ? badgeStyle : other.badgeStyle,
      iconStyle: t < 0.5 ? iconStyle : other.iconStyle,
      controlSurfaceAsset: t < 0.5
          ? controlSurfaceAsset
          : other.controlSurfaceAsset,
      controlSurfaceHoverAsset: t < 0.5
          ? controlSurfaceHoverAsset
          : other.controlSurfaceHoverAsset,
      outlinedControlSurfaceAsset: t < 0.5
          ? outlinedControlSurfaceAsset
          : other.outlinedControlSurfaceAsset,
      iconSurfaceAsset: t < 0.5 ? iconSurfaceAsset : other.iconSurfaceAsset,
      panelSurfaceAsset: t < 0.5 ? panelSurfaceAsset : other.panelSurfaceAsset,
      sidebarSurfaceAsset: t < 0.5
          ? sidebarSurfaceAsset
          : other.sidebarSurfaceAsset,
      navRailSurfaceAsset: t < 0.5
          ? navRailSurfaceAsset
          : other.navRailSurfaceAsset,
      messageSurfaceAsset: t < 0.5
          ? messageSurfaceAsset
          : other.messageSurfaceAsset,
      dividerSurfaceAsset: t < 0.5
          ? dividerSurfaceAsset
          : other.dividerSurfaceAsset,
      streamFrameSurfaceAsset: t < 0.5
          ? streamFrameSurfaceAsset
          : other.streamFrameSurfaceAsset,
    );
  }
}
