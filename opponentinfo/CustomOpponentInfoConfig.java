package net.runelite.client.plugins.opponentinfo;

import net.runelite.client.config.Config;
import net.runelite.client.config.ConfigGroup;
import net.runelite.client.config.ConfigItem;
import java.awt.Color;

@ConfigGroup("customopponentinfo")
public interface CustomOpponentInfoConfig extends Config {

	@ConfigItem(
			keyName = "showOpponentHealth",
			name = "Show Opponent Health",
			description = "Configures whether opponent health is shown"
	)
	default boolean showOpponentHealth() {
		return true;
	}

	@ConfigItem(
			keyName = "highlightNPCOutline",
			name = "Highlight NPC Outline",
			description = "Highlight the outline of the NPC"
	)
	default boolean highlightNPCOutline() {
		return true;
	}

	@ConfigItem(
			keyName = "npcOutlineColor",
			name = "NPC Outline Color",
			description = "Color of the NPC outline"
	)
	default Color npcOutlineColor() {
		return Color.YELLOW;
	}

	@ConfigItem(
			keyName = "showTileInfo",
			name = "Show Tile Information",
			description = "Display the tile coordinates of the NPC"
	)
	default boolean showTileInfo() {
		return true;
	}

	@ConfigItem(
			keyName = "showAnimationId",
			name = "Show Animation ID",
			description = "Display the animation ID of the NPC"
	)
	default boolean showAnimationId() {
		return true;
	}
}
