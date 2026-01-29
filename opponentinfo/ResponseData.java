package net.runelite.client.plugins.asd;

public class ResponseData {
    private Object data;
    private String error;

    public Object getData() {
        return data;
    }

    public String getError() {
        return error;
    }

    public void setData(Object data) {
        this.data = data;
    }

    public Object setError(String error) {
        this.error = error;
        return null;
    }
}