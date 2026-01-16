package net.runelite.client.plugins.asd;

import java.util.Map;

public class RequestData {
    private String function;
    private Map<String, Object> params;

    public String getFunction() {
        return function;
    }

    public Map<String, Object> getParams() {
        return params;
    }

    // Setters if needed
    public void setFunction(String function) {
        this.function = function;
    }

    public void setParams(Map<String, Object> params) {
        this.params = params;
    }
}