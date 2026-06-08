package net.runelite.client.plugins.asd;

import net.runelite.api.Client;
import net.runelite.api.GrandExchangeOffer;
import net.runelite.api.GrandExchangeOfferState;
import net.runelite.client.game.ItemManager;
import javax.inject.Inject;
import javax.inject.Singleton;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Singleton
public class GrandExchangeHandler {

    @Inject
    private Client client;

    @Inject
    private ItemManager itemManager;

    /**
     * Returns EVERY Grand Exchange offer (all 8 slots) with maximum possible information.
     */
    public Map<String, Object> getOffers() {
        Map<String, Object> result = new HashMap<>();
        List<Map<String, Object>> offersList = new ArrayList<>();

        GrandExchangeOffer[] offers = client.getGrandExchangeOffers();
        if (offers == null) {
            result.put("offers", offersList);
            result.put("totalSlots", 0);
            result.put("activeOffers", 0);
            return result;
        }

        for (int slot = 0; slot < offers.length; slot++) {
            GrandExchangeOffer offer = offers[slot];
            if (offer == null) {
                continue; // should never happen, but safety
            }

            Map<String, Object> offerData = new HashMap<>();
            offerData.put("slot", slot);

            GrandExchangeOfferState state = offer.getState();
            String stateName = (state != null) ? state.name() : "UNKNOWN";

            offerData.put("state", stateName);
            offerData.put("itemId", offer.getItemId());
            offerData.put("itemName", getItemName(offer.getItemId()));
            offerData.put("quantitySold", offer.getQuantitySold());
            offerData.put("totalQuantity", offer.getTotalQuantity());
            offerData.put("price", offer.getPrice());
            offerData.put("spent", offer.getSpent());

            // Buy vs Sell determination (based on official states)
            boolean isBuyOffer = (state == GrandExchangeOfferState.BUYING ||
                    state == GrandExchangeOfferState.BOUGHT ||
                    state == GrandExchangeOfferState.CANCELLED_BUY);
            offerData.put("isBuyOffer", isBuyOffer);

            // Extra convenience fields
            offerData.put("isEmpty", state == GrandExchangeOfferState.EMPTY);
            offerData.put("isComplete", state == GrandExchangeOfferState.BOUGHT || state == GrandExchangeOfferState.SOLD);
            offerData.put("isCancelled", state == GrandExchangeOfferState.CANCELLED_BUY ||
                    state == GrandExchangeOfferState.CANCELLED_SELL);
            offerData.put("progressPercent", calculateProgress(offer));

            offersList.add(offerData);
        }

        result.put("offers", offersList);
        result.put("totalSlots", offers.length);
        result.put("activeOffers", (int) offersList.stream()
                .filter(o -> !Boolean.TRUE.equals(o.get("isEmpty")))
                .count());

        return result;
    }

    private String getItemName(int itemId) {
        if (itemId <= 0) return "Empty slot";
        try {
            return itemManager.getItemComposition(itemId).getName();
        } catch (Exception e) {
            return "Unknown item (" + itemId + ")";
        }
    }

    private double calculateProgress(GrandExchangeOffer offer) {
        int total = offer.getTotalQuantity();
        if (total <= 0) return 0.0;
        return Math.round((double) offer.getQuantitySold() / total * 10000) / 100.0;
    }
}