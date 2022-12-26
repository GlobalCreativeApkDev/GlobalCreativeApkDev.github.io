package com.game.boxkeepups;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Scene;
import javafx.stage.Stage;

import java.io.IOException;

public class BoxKeepUpsApplication extends Application {
    @Override
    public void start(Stage stage) throws IOException {
        FXMLLoader fxmlLoader = new FXMLLoader(BoxKeepUpsApplication.class.getResource("boxkeepups-view.fxml"));
        Scene scene = new Scene(fxmlLoader.load(), 1080, 800);
        stage.setTitle("Box Keep Ups");
        stage.setScene(scene);
        stage.show();
    }

    public static void main(String[] args) {
        launch();
    }
}