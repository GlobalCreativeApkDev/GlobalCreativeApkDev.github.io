module com.game.reborninvasion {
    requires javafx.controls;
    requires javafx.fxml;

    requires com.almasb.fxgl.all;

    opens com.game.reborninvasion.client to javafx.fxml;
    exports com.game.reborninvasion.client;
}