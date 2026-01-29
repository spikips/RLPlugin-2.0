package net.runelite.client.plugins.asd;

import net.runelite.client.config.*;
import java.awt.Color;

@ConfigGroup("asd")
public interface AsdConfig extends Config
{
    // Tile Coordinates Section
    @ConfigSection(
            name = "Tile Coordinates",
            description = "Settings for Tile Coordinates Display",
            position = 1,
            closedByDefault = true
    )
    String tileCoordinatesSection = "tileCoordinates";

    @ConfigItem(
            keyName = "drawAllTileCoordinates",
            name = "Draw All Tile Coordinates",
            description = "Enable rendering of tile coordinates on all tiles",
            position = 1,
            section = tileCoordinatesSection
    )
    default boolean drawAllTileCoordinates()
    {
        return false;
    }

    @ConfigItem(
            keyName = "drawWalkableTileCoordinates",
            name = "Draw Walkable Tile Coordinates",
            description = "Enable rendering of tile coordinates only on walkable tiles",
            position = 2,
            section = tileCoordinatesSection
    )
    default boolean drawWalkableTileCoordinates()
    {
        return false;
    }

    @ConfigItem(
            keyName = "tileRadius",
            name = "Tile Radius",
            description = "Specify how many tiles around the player to display",
            position = 3,
            section = tileCoordinatesSection
    )
    default int tileRadius() {
        return 5;
    }
    @ConfigItem(
            keyName = "showClientCoordinates",
            name = "Show Client Screen Coordinates",
            description = "Include the tile's x,y position on the client screen under the tile's world coordinates",
            position = 4,
            section = tileCoordinatesSection
    )
    default boolean showClientCoordinates()
    {
        return false;
    }

    // Player Status Overlay Section
    @ConfigSection(
            name = "Player Status Overlay",
            description = "Settings for Player Status Overlay",
            position = 2,
            closedByDefault = true
    )
    String playerStatusSection = "playerStatus";

    @ConfigItem(
            keyName = "locationEnabled",
            name = "Enable Location",
            description = "Show player location",
            position = 1,
            section = playerStatusSection
    )
    default boolean locationEnabled()
    {
        return false;
    }

    @ConfigItem(
            keyName = "healthEnabled",
            name = "Enable Health and Prayer",
            description = "Show HP and prayer levels",
            position = 2,
            section = playerStatusSection
    )
    default boolean healthEnabled()
    {
        return false;
    }

    @ConfigItem(
            keyName = "runEnergyEnabled",
            name = "Enable Run Energy",
            description = "Show run energy level",
            position = 3,
            section = playerStatusSection
    )
    default boolean runEnergyEnabled()
    {
        return false;
    }

    @ConfigItem(
            keyName = "weightEnabled",
            name = "Enable Weight",
            description = "Show player weight",
            position = 4,
            section = playerStatusSection
    )
    default boolean weightEnabled()
    {
        return false;
    }
    @ConfigItem(
            keyName = "playerAnimationEnabled",
            name = "Enable Player Animation",
            description = "Show the player's current animation",
            position = 5,
            section = playerStatusSection
    )
    default boolean playerAnimationEnabled() {
        return false;
    }
    @ConfigItem(
            keyName = "showClientCamera",
            name = "Show Client Camera Info",
            description = "Display the client's current pitch, yaw, and zoom level",
            position = 6,
            section = playerStatusSection
    )
    default boolean showClientCamera()
    {
        return false;
    }
    @ConfigItem(
            keyName = "showClientTick",
            name = "Show Client Tick",
            description = "Display the current client tick",
            position = 7,
            section = playerStatusSection
    )
    default boolean showClientTick()
    {
        return false;
    }

    // Quest and Skill States Section
    @ConfigSection(
            name = "Quest and Skill States",
            description = "Settings for Quest States and Skill Levels",
            position = 3,
            closedByDefault = true
    )
    String questSkillSection = "questSkillSection";

    @ConfigItem(
            keyName = "questStatesEnabled",
            name = "Enable Quest States",
            description = "Extract and log quest states",
            position = 1,
            section = questSkillSection
    )
    default boolean questStatesEnabled()
    {
        return false;
    }

    @ConfigItem(
            keyName = "skillLevelsEnabled",
            name = "Enable Skill Levels",
            description = "Extract and log skill levels and XP",
            position = 2,
            section = questSkillSection
    )
    default boolean skillLevelsEnabled()
    {
        return false;
    }

    // Equipped Gear Section
    @ConfigSection(
            name = "Equipped Gear",
            description = "Settings for Equipped Gear",
            position = 4,
            closedByDefault = true
    )
    String equippedGearSection = "equippedGearSection";

    @ConfigItem(
            keyName = "equippedGearEnabled",
            name = "Enable Equipped Gear",
            description = "Extract and log currently equipped gear",
            position = 1,
            section = equippedGearSection
    )
    default boolean equippedGearEnabled()
    {
        return false;
    }

    // Chat Messages Section
    @ConfigSection(
            name = "Chat Messages",
            description = "Settings for Chat Messages",
            position = 5,
            closedByDefault = true
    )
    String chatMessagesSection = "chatMessagesSection";

    @ConfigItem(
            keyName = "chatMessagesEnabled",
            name = "Enable Chat Messages",
            description = "Extract and log recent chat messages",
            position = 1,
            section = chatMessagesSection
    )
    default boolean chatMessagesEnabled()
    {
        return false;
    }

    // NPC Section
    @ConfigSection(
            name = "NPC Highlight",
            description = "Settings for NPC Highlight",
            position = 6,
            closedByDefault = true
    )
    String npcSection = "npcSection";

    @ConfigItem(
            keyName = "npcHighlightEnabled",
            name = "Enable NPC Highlight",
            description = "Enable highlighting of NPCs",
            position = 1,
            section = npcSection
    )
    default boolean npcHighlightEnabled()
    {
        return false;
    }

    @ConfigItem(
            keyName = "showNPCInfo",
            name = "Show NPC Info",
            description = "Display NPC's name, ID, and location above the NPC and print to console",
            position = 2,
            section = npcSection
    )
    default boolean showNPCInfo()
    {
        return true;
    }

    @ConfigItem(
            keyName = "npcNameFilter",
            name = "NPC Name Filter",
            description = "Only display NPCs matching the given names (comma-separated)",
            position = 3,
            section = npcSection
    )
    default String npcNameFilter() {
        return "";
    }

    @ConfigItem(
            keyName = "highlightNPCOutline",
            name = "Highlight NPC Outline",
            description = "Draw outlines around NPCs",
            position = 4,
            section = npcSection
    )
    default boolean highlightNPCOutline()
    {
        return true;
    }

    @ConfigItem(
            keyName = "highlightNPCTile",
            name = "Highlight NPC Tile",
            description = "Draw a highlight on the tile where the NPC is standing",
            position = 5,
            section = npcSection
    )
    default boolean highlightNPCTile()
    {
        return true;
    }

    @ConfigItem(
            keyName = "npcTextSize",
            name = "NPC Text Size",
            description = "Adjust the size of the text displayed over NPCs",
            position = 6,
            section = npcSection
    )
    default int npcTextSize()
    {
        return 12;
    }

    @ConfigItem(
            keyName = "npcTextColor",
            name = "NPC Text Color",
            description = "Choose the color of the NPC text",
            position = 7,
            section = npcSection
    )
    default Color npcTextColor()
    {
        return Color.WHITE;
    }

    @Alpha
    @ConfigItem(
            keyName = "npcOutlineColor",
            name = "NPC Outline Color",
            description = "Choose the color of the NPC outline",
            position = 8,
            section = npcSection
    )
    default Color npcOutlineColor()
    {
        return new Color(255, 0, 0, 255); // Default opaque red
    }

    @ConfigItem(
            keyName = "npcTileColor",
            name = "NPC Tile Color",
            description = "Choose the color of the NPC tile highlight",
            position = 9,
            section = npcSection
    )
    default Color npcTileColor()
    {
        return new Color(255, 255, 0); // Default yellow
    }

    @ConfigItem(
            keyName = "logAggressiveNpcs",
            name = "Log Aggressive NPCs",
            description = "Log NPCs aggressive towards you",
            position = 10,
            section = npcSection
    )
    default boolean logAggressiveNpcs() {
        return false;
    }

    // Inventory Item IDs Section
    @ConfigSection(
            name = "Inventory Item IDs",
            description = "Settings for Inventory Item IDs",
            position = 7,
            closedByDefault = true
    )
    String inventorySection = "inventorySection";

    @ConfigItem(
            keyName = "inventoryItemIDsEnabled",
            name = "Enable Inventory Item IDs",
            description = "Enable logging of inventory item IDs and their positions",
            position = 1,
            section = inventorySection
    )
    default boolean inventoryItemIDsEnabled() {
        return false;
    }

    @ConfigItem(
            keyName = "displayItemIDOverlays",
            name = "Display Item ID Overlays",
            description = "Enable displaying item IDs over inventory items",
            position = 2,
            section = inventorySection
    )
    default boolean displayItemIDOverlays() {
        return false;
    }

    @ConfigItem(
            keyName = "inventoryItemTextSize",
            name = "Inventory Item Text Size",
            description = "Adjust the size of the text displayed over inventory items",
            position = 3,
            section = inventorySection
    )
    default int inventoryItemTextSize()
    {
        return 12;
    }

    @ConfigItem(
            keyName = "inventoryItemTextColor",
            name = "Inventory Item Text Color",
            description = "Choose the color of the inventory item text",
            position = 4,
            section = inventorySection
    )
    default Color inventoryItemTextColor()
    {
        return Color.WHITE;
    }

    // Object IDs Section
    @ConfigSection(
            name = "Object IDs",
            description = "Settings for Object IDs",
            position = 8,
            closedByDefault = true
    )
    String objectIDsSection = "objectIDsSection";

    @ConfigItem(
            keyName = "extractLocalObjectsEnabled",
            name = "Enable Object IDs",
            description = "Enable displaying local object IDs",
            position = 1,
            section = objectIDsSection
    )
    default boolean extractLocalObjectsEnabled()
    {
        return false;
    }

    @ConfigItem(
            keyName = "interactableActions",
            name = "Interactable Actions",
            description = "Specify actions that qualify an object as interactable, separated by commas",
            position = 2,
            section = objectIDsSection
    )
    default String interactableActions() {
        return "Open,Close,Search,Talk-to,Climb,Enter";
    }

    @ConfigItem(
            keyName = "objectIdTextSize",
            name = "Object ID Text Size",
            description = "Adjust the size of the text displayed for object IDs",
            position = 3,
            section = objectIDsSection
    )
    default int objectIdTextSize() {
        return 10;
    }

    @ConfigItem(
            keyName = "objectIdTextColor",
            name = "Object ID Text Color",
            description = "Color of the object ID text",
            position = 4,
            section = objectIDsSection
    )
    default Color objectIdTextColor() {
        return Color.WHITE;
    }

    @Alpha
    @ConfigItem(
            keyName = "objectOutlineColor",
            name = "Object Outline Color",
            description = "Choose the color of the object outlines",
            position = 5,
            section = objectIDsSection
    )
    default Color objectOutlineColor()
    {
        return new Color(255, 0, 0, 255); // Default opaque red
    }

    @ConfigItem(
            keyName = "objectIdFont",
            name = "Object ID Font",
            description = "Font style for object ID text",
            position = 6,
            section = objectIDsSection
    )
    default String objectIdFont() {
        return "Arial";
    }

    // Game Object Highlight Section
    @ConfigSection(
            name = "Game Object Highlight",
            description = "Settings for Game Object Highlight",
            position = 9,
            closedByDefault = true
    )
    String gameObjectSection = "gameObjectSection";

    @ConfigItem(
            keyName = "gameObjectHighlightEnabled",
            name = "Enable Game Object Highlight",
            description = "Enable highlighting of game objects",
            position = 1,
            section = gameObjectSection
    )
    default boolean gameObjectHighlightEnabled()
    {
        return false;
    }

    @ConfigItem(
            keyName = "gameObjectFilter",
            name = "Game Object Filter",
            description = "Display objects matching these names or IDs (comma-separated)",
            position = 2,
            section = gameObjectSection
    )
    default String gameObjectFilter() {
        return "";
    }

    @Alpha
    @ConfigItem(
            keyName = "gameObjectOutlineColor",
            name = "Game Object Outline Color",
            description = "Color of the game object outline",
            position = 3,
            section = gameObjectSection
    )
    default Color gameObjectOutlineColor()
    {
        return new Color(0, 255, 0, 255); // Default opaque green
    }

    @ConfigItem(
            keyName = "gameObjectTextColor",
            name = "Game Object Text Color",
            description = "Color of the game object text",
            position = 4,
            section = gameObjectSection
    )
    default Color gameObjectTextColor()
    {
        return Color.WHITE;
    }

    @ConfigItem(
            keyName = "gameObjectTextSize",
            name = "Game Object Text Size",
            description = "Size of the text displayed over game objects",
            position = 5,
            section = gameObjectSection
    )
    default int gameObjectTextSize()
    {
        return 12;
    }

    // Under Attack Indicator Section
    @ConfigSection(
            name = "Under Attack Indicator",
            description = "Settings for under attack indicator",
            position = 10,
            closedByDefault = true
    )
    String underAttackSection = "underAttack";

    @ConfigItem(
            keyName = "enableUnderAttackIndicator",
            name = "Enable Targeting Indicator",
            description = "Show indicator for when targeted (even if blocked)",
            position = 1,
            section = underAttackSection
    )
    default boolean enableUnderAttackIndicator()
    {
        return true;
    }

    @ConfigItem(
            keyName = "enableReachableIndicator",
            name = "Enable Reachable Indicator",
            description = "Show indicator for when targeted NPC can actually reach/hit you (obstacles checked)",
            position = 2,
            section = underAttackSection
    )
    default boolean enableReachableIndicator()
    {
        return true;
    }

    @Alpha
    @ConfigItem(
            keyName = "underAttackColor",
            name = "Under Attack Color",
            description = "Color when under attack/reachable",
            position = 3,
            section = underAttackSection
    )
    default Color underAttackColor()
    {
        return new Color(0, 255, 0, 255); // Default opaque green
    }

    @Alpha
    @ConfigItem(
            keyName = "notUnderAttackColor",
            name = "Not Under Attack Color",
            description = "Color when not under attack/reachable",
            position = 4,
            section = underAttackSection
    )
    default Color notUnderAttackColor()
    {
        return new Color(255, 0, 0, 255); // Default opaque red
    }

    // Mouse Hover Interaction Options Section
    @ConfigSection(
            name = "Mouse Hover Interaction Options",
            description = "Settings for displaying interaction options when hovering over locations",
            position = 11,
            closedByDefault = true
    )
    String mouseHoverSection = "mouseHoverSection";

    @ConfigItem(
            keyName = "enableMouseHoverInteractOptions",
            name = "Enable Mouse Hover Interact Options",
            description = "Display interaction options at the current mouse location",
            position = 1,
            section = mouseHoverSection
    )
    default boolean enableMouseHoverInteractOptions()
    {
        return false;
    }

    @ConfigItem(
            keyName = "interactOptionFontSize",
            name = "Interact Option Font Size",
            description = "Font size for interact option display",
            position = 2,
            section = mouseHoverSection
    )
    default int interactOptionFontSize()
    {
        return 12;
    }

    @ConfigItem(
            keyName = "interactOptionColor",
            name = "Interact Option Color",
            description = "Color for interact option text",
            position = 3,
            section = mouseHoverSection
    )
    default Color interactOptionColor()
    {
        return Color.WHITE;
    }

    // Minimap Hover Section
    @ConfigSection(
            name = "Minimap Hover",
            description = "Settings for Minimap Hover Tile Display",
            position = 12,
            closedByDefault = true
    )
    String minimapHoverSection = "minimapHoverSection";

    @ConfigItem(
            keyName = "enableMinimapHoverTile",
            name = "Enable Minimap Hover Tile",
            description = "Show tile coordinates when hovering over the minimap",
            position = 1,
            section = minimapHoverSection
    )
    default boolean enableMinimapHoverTile()
    {
        return false;
    }

    @ConfigItem(
            keyName = "minimapHoverTextSize",
            name = "Minimap Hover Text Size",
            description = "Font size for minimap hover tile coordinates",
            position = 2,
            section = minimapHoverSection
    )
    default int minimapHoverTextSize()
    {
        return 10; // Small text size
    }

    @ConfigItem(
            keyName = "minimapHoverTextColor",
            name = "Minimap Hover Text Color",
            description = "Color of the minimap hover tile text",
            position = 3,
            section = minimapHoverSection
    )
    default Color minimapHoverTextColor()
    {
        return Color.WHITE;
    }

    @Alpha
    @ConfigItem(
            keyName = "minimapHoverTextShadowColor",
            name = "Minimap Hover Text Shadow Color",
            description = "Color of the shadow for minimap hover tile text",
            position = 4,
            section = minimapHoverSection
    )
    default Color minimapHoverTextShadowColor()
    {
        return new Color(0, 0, 0, 255); // Black shadow
    }

    // Varbit Monitoring Section
    @ConfigSection(
            name = "Varbit Monitoring",
            description = "Settings for monitoring varbit changes",
            position = 13,
            closedByDefault = true
    )
    String varbitMonitoringSection = "varbitMonitoringSection";

    @ConfigItem(
            keyName = "varbitMonitoringEnabled",
            name = "Enable Varbit Monitoring",
            description = "Listen for varbit changes and log to console",
            position = 1,
            section = varbitMonitoringSection
    )
    default boolean varbitMonitoringEnabled()
    {
        return false;
    }

    @ConfigItem(
            keyName = "includeVarbits",
            name = "Include Varbits",
            description = "Comma-separated varbit IDs to monitor (leave empty for all)",
            position = 2,
            section = varbitMonitoringSection
    )
    default String includeVarbits() {
        return "";
    }

    @ConfigItem(
            keyName = "excludeVarbits",
            name = "Exclude Varbits",
            description = "Comma-separated varbit IDs to ignore",
            position = 3,
            section = varbitMonitoringSection
    )
    default String excludeVarbits() {
        return "";
    }

    @ConfigItem(
            keyName = "enableVarbitNames",
            name = "Enable Varbit Names",
            description = "Include varbit names and descriptions in logs",
            position = 4,
            section = varbitMonitoringSection
    )
    default boolean enableVarbitNames()
    {
        return true;
    }

    @ConfigItem(
            keyName = "varbitChangeLogger",
            name = "Varbit Change Logger",
            description = "Log all varbit changes to console and expose via socket for debugging",
            position = 5,
            section = varbitMonitoringSection
    )
    default boolean varbitChangeLogger() { return false; }

    // Player Highlight Section
    @ConfigSection(
            name = "Player Highlight",
            description = "Settings for Player Highlight",
            position = 14,
            closedByDefault = true
    )
    String playerSection = "playerSection";

    @ConfigItem(
            keyName = "playerHighlightEnabled",
            name = "Enable Player Highlight",
            description = "Enable highlighting of other players",
            position = 1,
            section = playerSection
    )
    default boolean playerHighlightEnabled()
    {
        return false;
    }

    @ConfigItem(
            keyName = "showPlayerInfo",
            name = "Show Player Info",
            description = "Display player's name, ID, combat level, and location above the player",
            position = 2,
            section = playerSection
    )
    default boolean showPlayerInfo()
    {
        return true;
    }

    @ConfigItem(
            keyName = "playerNameFilter",
            name = "Player Name Filter",
            description = "Only display players matching the given names (comma-separated)",
            position = 3,
            section = playerSection
    )
    default String playerNameFilter() {
        return "";
    }

    @ConfigItem(
            keyName = "highlightPlayerOutline",
            name = "Highlight Player Outline",
            description = "Draw outlines around players",
            position = 4,
            section = playerSection
    )
    default boolean highlightPlayerOutline()
    {
        return false;
    }

    @ConfigItem(
            keyName = "highlightPlayerTile",
            name = "Highlight Player Tile",
            description = "Draw a highlight on the tile where the player is standing",
            position = 5,
            section = playerSection
    )
    default boolean highlightPlayerTile()
    {
        return true;
    }

    @ConfigItem(
            keyName = "playerTextSize",
            name = "Player Text Size",
            description = "Adjust the size of the text displayed over players",
            position = 6,
            section = playerSection
    )
    default int playerTextSize()
    {
        return 10;
    }

    @ConfigItem(
            keyName = "playerTextColor",
            name = "Player Text Color",
            description = "Choose the color of the player text",
            position = 7,
            section = playerSection
    )
    default Color playerTextColor()
    {
        return Color.WHITE;
    }

    @Alpha
    @ConfigItem(
            keyName = "playerOutlineColor",
            name = "Player Outline Color",
            description = "Choose the color of the player outline",
            position = 8,
            section = playerSection
    )
    default Color playerOutlineColor()
    {
        return new Color(0, 255, 255, 255); // Default opaque cyan
    }

    @ConfigItem(
            keyName = "playerTileColor",
            name = "Player Tile Color",
            description = "Choose the color of the player tile highlight",
            position = 9,
            section = playerSection
    )
    default Color playerTileColor()
    {
        return new Color(0, 255, 255); // Default cyan
    }

    @ConfigItem(
            keyName = "playerRadius",
            name = "Player Radius",
            description = "Specify how many tiles around the local player to highlight others",
            position = 10,
            section = playerSection
    )
    default int playerRadius() {
        return 10;
    }

    // Click Logging Section
    @ConfigSection(
            name = "Click Logging",
            description = "Settings for tracking and exposing mouse clicks",
            position = 15,
            closedByDefault = true
    )
    String clickSection = "clickLogging";

    @ConfigItem(
            keyName = "enableClickLogging",
            name = "Enable Click Logging",
            description = "Log and expose left/right/middle clicks via socket",
            position = 1,
            section = clickSection
    )
    default boolean enableClickLogging() {
        return false;
    }

    // Colors Section
    @ConfigSection(
            name = "Colors",
            description = "Customize colors for various elements",
            position = 99,
            closedByDefault = true
    )
    String colorSettingsSection = "colorSettings";

    @Alpha
    @ConfigItem(
            keyName = "tileOutlineColor",
            name = "Tile Outline Color",
            description = "Choose the color of the tile outlines",
            position = 1,
            section = colorSettingsSection
    )
    default Color tileOutlineColor() {
        return new Color(255, 255, 0, 255); // Default opaque yellow
    }

    @ConfigItem(
            keyName = "tileTextColor",
            name = "Tile Text Color",
            description = "Color of the text displayed on tiles",
            position = 2,
            section = colorSettingsSection
    )
    default Color tileTextColor() {
        return Color.WHITE;
    }

    @ConfigItem(
            keyName = "overlayTextColor",
            name = "Overlay Text Color",
            description = "Choose the color of the overlay text",
            position = 3,
            section = colorSettingsSection
    )
    default Color overlayTextColor() {
        return Color.WHITE;
    }

    @Alpha
    @ConfigItem(
            keyName = "overlayBackgroundColor",
            name = "Overlay Background Color",
            description = "Background color of the overlays",
            position = 5,
            section = colorSettingsSection
    )
    default Color overlayBackgroundColor() {
        return new Color(64, 64, 64, 100); // Dark gray with opacity of 100
    }

    @Alpha
    @ConfigItem(
            keyName = "overlayBorderColor",
            name = "Overlay Border Color",
            description = "Choose the color of the overlay border, including transparency",
            position = 11,
            section = colorSettingsSection
    )
    default Color overlayBorderColor()
    {
        return new Color(255, 255, 255, 255); // Default white, fully opaque
    }

    @Alpha
    @ConfigItem(
            keyName = "overlayTextShadowColor",
            name = "Overlay Text Shadow Color",
            description = "Choose the color of the overlay text shadow",
            position = 12,
            section = colorSettingsSection
    )
    default Color overlayTextShadowColor()
    {
        return new Color(0, 0, 0, 255); // Default black, fully opaque
    }

    // Text Sizes Section
    @ConfigSection(
            name = "Text Sizes",
            description = "Adjust text sizes for overlay elements",
            position = 100,
            closedByDefault = true
    )
    String textSizeSettingsSection = "textSizeSettings";

    @ConfigItem(
            keyName = "overlayTextSize",
            name = "Overlay Text Size",
            description = "Adjust the size of the text displayed in the overlay",
            position = 1,
            section = textSizeSettingsSection
    )
    default int overlayTextSize() {
        return 12;
    }

    @ConfigItem(
            keyName = "tileTextSize",
            name = "Tile Text Size",
            description = "Adjust the size of the text displayed on tiles",
            position = 2,
            section = textSizeSettingsSection
    )
    default int tileTextSize() {
        return 10;
    }
}