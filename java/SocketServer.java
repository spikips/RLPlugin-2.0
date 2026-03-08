package net.runelite.client.plugins.asd;

import com.google.gson.Gson;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import javax.inject.Singleton;
import lombok.extern.slf4j.Slf4j;
import javax.inject.Inject;

import net.runelite.api.*;
import net.runelite.api.coords.LocalPoint;
import net.runelite.api.coords.WorldPoint;
import net.runelite.api.events.GameObjectSpawned;
import net.runelite.api.events.AnimationChanged;
import net.runelite.client.callback.ClientThread;
import net.runelite.client.game.ItemManager;
import net.runelite.client.plugins.opponentinfo.CustomOpponentInfoPlugin;
import java.io.*;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.CountDownLatch;

@Slf4j
@Singleton
public class SocketServer {
    @Inject
    private ClientThread clientThread;

    @Inject
    private CannonHandler cannonHandler;  // New injection

    private ServerSocket serverSocket;
    private boolean running = false;
    private final int port = 6565;
    private final String authToken = "jQ8IHav3zA3HuH4";
    private final Gson gson = new Gson();

    @Inject
    private Client client;

    @Inject
    private ItemManager itemManager;

    @Inject
    private PlayerHandler playerHandler;

    @Inject
    private EntityHandler entityHandler;

    @Inject
    private WorldHandler worldHandler;

    @Inject
    private GameStateHandler gameStateHandler;

    @Inject
    private InterfaceHandler interfaceHandler;

    @Inject
    private WeaponHandler weaponHandler;

    @Inject
    private PrayerHandler prayerHandler;

    @Inject
    private MinimapHoverHandler minimapHoverHandler;

    @Inject
    private LogoutHandler logoutHandler;

    @Inject
    private AsdPlugin plugin;

    @Inject
    private GetVarbits getVarbits;

    @Inject
    private PlayersHandler playersHandler;

    @Inject
    private MainOverlay mainOverlay;

    @Inject
    private ClickHandler clickHandler;

    @Inject
    private GrandExchangeHandler grandExchangeHandler;

    private final List<BufferedWriter> subscribedClients = new CopyOnWriteArrayList<>();

    public void setCustomOpponentInfoPlugin(CustomOpponentInfoPlugin customOpponentInfoPlugin) {
        playerHandler.setCustomOpponentInfoPlugin(customOpponentInfoPlugin);
        entityHandler.setCustomOpponentInfoPlugin(customOpponentInfoPlugin);
    }

    public void startServer() {
        try {
            serverSocket = new ServerSocket(port);
            running = true;
            new Thread(this::listenForClients).start();
            log.info("SocketServer started on port {}", port);
        } catch (IOException e) {
            log.error("Error starting server: ", e);
        }
    }

    private void listenForClients() {
        while (running) {
            try {
                Socket clientSocket = serverSocket.accept();
                if (isLocalConnection(clientSocket)) {
                    handleClient(clientSocket);
                } else {
                    clientSocket.close();
                    log.warn("Rejected non-local connection from {}", clientSocket.getInetAddress());
                }
            } catch (IOException e) {
                if (running) {
                    log.error("Error accepting client connection: ", e);
                }
            }
        }
    }

    private boolean isLocalConnection(Socket socket) {
        return socket.getInetAddress().isLoopbackAddress();
    }

    private void handleClient(Socket clientSocket) {
        new Thread(() -> {
            try (
                    BufferedReader reader = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
                    BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(clientSocket.getOutputStream()))
            ) {
                String requestLine = reader.readLine();
                if (requestLine != null && requestLine.startsWith(authToken)) {
                    String jsonRequest = requestLine.substring(authToken.length()).trim();
                    String jsonResponse = processRequest(jsonRequest);
                    writer.write(jsonResponse);
                    writer.newLine();
                    writer.flush();
                } else {
                    writer.write("Unauthorized");
                    writer.newLine();
                    writer.flush();
                    log.warn("Unauthorized access attempt from {}", clientSocket.getInetAddress());
                }
            } catch (IOException e) {
                log.error("Error handling client: ", e);
            } finally {
                try {
                    clientSocket.close();
                } catch (IOException e) {
                    log.error("Error closing client socket: ", e);
                }
            }
        }).start();
    }

    private String processRequest(String jsonRequest) {
        final String[] resultHolder = new String[1];
        CountDownLatch latch = new CountDownLatch(1);

        clientThread.invokeLater(() -> {
            try {
                RequestData requestData = gson.fromJson(jsonRequest, RequestData.class);
                ResponseData responseData = new ResponseData();
                log.info("Received request: {}", jsonRequest);

                String function = requestData.getFunction();
                Map<String, Object> params = requestData.getParams();

                switch (function) {
                    case "player":
                        Map<String, Object> playerParams = params != null ? params : new HashMap<>();
                        playerParams.putIfAbsent("prayer", true);
                        responseData.setData(playerHandler.handle("player", playerParams));
                        break;
                    case "quest":
                    case "stats":
                    case "gear":
                    case "chat":
                        responseData.setData(playerHandler.handle(function, params));
                        break;

                    case "npc":
                    case "opponentInfo":
                    case "pick":
                        responseData.setData(entityHandler.handle(function, params));
                        break;
                    case "gameObject":
                    case "tile":
                    case "walkable_tile":
                    case "findArea":
                        responseData.setData(worldHandler.handle(function, params));
                        break;
                    case "local_object":
                        responseData.setData(mainOverlay.findLocalObjects(params));
                        break;
                    case "gametick":
                    case "zoom":
                    case "mainMenu":
                    case "gameState":
                        responseData.setData(gameStateHandler.handle(function, params));
                        break;
                    case "inventory":
                    case "bankItems":
                    case "clickWidget":
                    case "interactOptions":
                        responseData.setData(interfaceHandler.handle(function, params));
                        break;
                    case "combat_style":
                        responseData.setData(weaponHandler.getCurrentCombatInfo());
                        break;
                    case "prayers":
                        responseData.setData(prayerHandler.getActivePrayers());
                        break;
                    case "varbits":
                        responseData.setData(getVarbits.getVarbitValues(params));
                        break;
                    case "npc_agro":
                        responseData.setData(plugin.getAggressiveNpcs(params));
                        break;
                    case "set_npc_config":
                        plugin.setNpcConfig(params);
                        responseData.setData("success");
                        break;
                    case "logout":
                        responseData.setData(logoutHandler.handle(function, params));
                        break;
                    case "minimapHoverTile":
                    case "minimapTilePoint":
                        responseData.setData(minimapHoverHandler.handle(function, params));
                        break;
                    case "players":
                        responseData.setData(playersHandler.handle(function, params));
                        break;
                    case "target_npc":
                        responseData.setData(getPlayerTarget());
                        break;
                    case "cannon_data":
                        responseData.setData(cannonHandler.getCannonData());
                        break;
                    case "varbit_changes":
                        responseData.setData(plugin.getVariableChanges()); // Change from getVarbitChanges()
                        break;
                    case "slayer_task_remaining":
                        responseData.setData(getSlayerTaskRemaining());
                        break;
                    case "get_varbits":
                        responseData.setData(getVarbits.getVarbitValues(params));
                        break;
                    case "click":
                        if (params.containsKey("function")) {
                            String subFunction = (String) params.get("function");
                            responseData.setData(clickHandler.handle(subFunction, params));
                        } else {
                            responseData.setError("Missing 'function' parameter for click handler");
                        }
                        break;
                    case "grand_exchange":
                    case "ge":
                    case "ge_offers":
                        responseData.setData(grandExchangeHandler.getOffers());
                        break;
                    default:
                        responseData.setError("Unknown function: " + function);

                }
                resultHolder[0] = gson.toJson(responseData);
                log.info("Response data: {}", resultHolder[0]);
            } catch (Exception e) {
                log.error("Error processing request: ", e);
                ResponseData errorResponse = new ResponseData();
                errorResponse.setError("Error processing request: " + e.getMessage());
                resultHolder[0] = gson.toJson(errorResponse);
            } finally {
                latch.countDown();
            }
        });

        try {
            latch.await();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            ResponseData errorResponse = new ResponseData();
            errorResponse.setError("Error processing request: " + e.getMessage());
            return gson.toJson(errorResponse);
        }

        return resultHolder[0];
    }

    private int getSlayerTaskRemaining() {
        return client.getVarpValue(394);  // VarPlayer 394: Remaining Slayer kills
    }

    private Map<String, Object> getPlayerTarget() {
        Actor interacting = client.getLocalPlayer().getInteracting();
        if (interacting instanceof NPC) {
            NPC npc = (NPC) interacting;
            Map<String, Object> data = new HashMap<>();
            data.put("name", npc.getName());
            data.put("id", npc.getId());
            data.put("index", npc.getIndex());
            data.put("healthRatio", npc.getHealthRatio());
            data.put("healthScale", npc.getHealthScale());
            data.put("animation", npc.getAnimation());

            WorldPoint wp = npc.getWorldLocation();
            Map<String, Integer> loc = new HashMap<>();
            loc.put("x", wp.getX());
            loc.put("y", wp.getY());
            loc.put("plane", wp.getPlane());
            data.put("location", loc);

            LocalPoint lp = npc.getLocalLocation();
            if (lp != null) {
                Point canvasPoint = Perspective.localToCanvas(client, lp, wp.getPlane(), npc.getLogicalHeight() / 2);
                if (canvasPoint != null) {
                    Map<String, Integer> mp = new HashMap<>();
                    mp.put("x", canvasPoint.getX());
                    mp.put("y", canvasPoint.getY());
                    data.put("middle_point", mp);
                }
            }
            return data;
        }
        return null; // No target
    }

    public void stopServer() {
        running = false;
        try {
            if (serverSocket != null) {
                serverSocket.close();
                log.info("SocketServer stopped");
            }
        } catch (IOException e) {
            log.error("Error stopping server: ", e);
        }
    }
}