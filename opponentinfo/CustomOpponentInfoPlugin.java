package net.runelite.client.plugins.opponentinfo;

import com.google.inject.Provides;
import java.time.Duration;
import java.time.Instant;
import javax.inject.Inject;
import javax.inject.Singleton;
import lombok.AccessLevel;
import lombok.Getter;
import net.runelite.api.Actor;
import net.runelite.api.Client;
import net.runelite.api.GameState;
import net.runelite.api.MenuAction;
import net.runelite.api.MenuEntry;
import net.runelite.api.NPC;
import net.runelite.api.events.GameStateChanged;
import net.runelite.api.events.GameTick;
import net.runelite.api.events.InteractingChanged;
import net.runelite.api.events.MenuEntryAdded;
import net.runelite.client.config.ConfigManager;
import net.runelite.client.eventbus.Subscribe;
import net.runelite.client.plugins.Plugin;
import net.runelite.client.plugins.PluginDescriptor;
import net.runelite.client.plugins.asd.SocketServer;
import net.runelite.client.ui.overlay.OverlayManager;

@PluginDescriptor(
        name = "Custom Opponent Info",
        description = "Show HP of the NPC you are fighting and highlight it",
        tags = {"combat", "health", "hitpoints", "npcs", "overlay"}
)
@Singleton
public class CustomOpponentInfoPlugin extends Plugin {
    private static final Duration WAIT = Duration.ofSeconds(5);

    @Inject
    private Client client;

    @Inject
    private CustomOpponentInfoConfig config;

    @Inject
    private OverlayManager overlayManager;

    @Inject
    private CustomOpponentInfoOverlay customOpponentInfoOverlay;

    @Inject
    private SocketServer pluginSocketServer;  // Ensure server is injected

    @Getter(AccessLevel.PACKAGE)
    private Actor lastOpponent;

    @Getter(AccessLevel.PACKAGE)
    private Instant lastTime;

    @Provides
    CustomOpponentInfoConfig provideConfig(ConfigManager configManager) {
        return configManager.getConfig(CustomOpponentInfoConfig.class);
    }

    @Override
    protected void startUp() throws Exception {
        overlayManager.add(customOpponentInfoOverlay);
        // Initialize and start the server
        pluginSocketServer.setCustomOpponentInfoPlugin(this);
        pluginSocketServer.startServer();
    }

    @Override
    protected void shutDown() throws Exception {
        lastOpponent = null;
        lastTime = null;
        overlayManager.remove(customOpponentInfoOverlay);
        // Shutdown the server
        pluginSocketServer.stopServer();
    }

    @Subscribe
    public void onInteractingChanged(InteractingChanged event) {
        if (event.getSource() != client.getLocalPlayer()) {
            return;
        }

        Actor opponent = event.getTarget();

        if (opponent == null) {
            lastTime = Instant.now();
            return;
        }

        lastOpponent = opponent;
    }

    @Subscribe
    public void onGameTick(GameTick gameTick) {
        if (lastOpponent != null && lastTime != null && client.getLocalPlayer().getInteracting() == null) {
            if (Duration.between(lastTime, Instant.now()).compareTo(WAIT) > 0) {
                lastOpponent = null;
            }
        }
    }

    @Subscribe
    public void onMenuEntryAdded(MenuEntryAdded menuEntryAdded) {
        if (menuEntryAdded.getType() != MenuAction.NPC_SECOND_OPTION.getId()
                || !menuEntryAdded.getOption().equals("Attack")
                || !config.showOpponentHealth()) {
            return;
        }

        NPC npc = menuEntryAdded.getMenuEntry().getNpc();
        if (npc == null) {
            return;
        }

        if (npc.getInteracting() == client.getLocalPlayer() || lastOpponent == npc) {
            MenuEntry[] menuEntries = client.getMenuEntries();
            menuEntries[menuEntries.length - 1].setTarget("*" + menuEntries[menuEntries.length - 1].getTarget());
        }
    }

    @Subscribe
    public void onGameStateChanged(GameStateChanged gameStateChanged) {
        if (gameStateChanged.getGameState() != GameState.LOGGED_IN) {
            return;
        }
    }

    public Client getClient() {
        return client;
    }

    // Make this method public
    public Actor getLastOpponent() {
        return lastOpponent;
    }
}
