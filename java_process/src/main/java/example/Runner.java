package example;

import com.google.gson.Gson;
import com.rabbitmq.client.*;


import java.io.*;
import java.net.URISyntaxException;
import java.nio.charset.StandardCharsets;
import java.security.KeyManagementException;
import java.security.NoSuchAlgorithmException;
import java.util.concurrent.TimeoutException;
import java.util.zip.GZIPInputStream;
import java.util.zip.GZIPOutputStream;

public class Runner {
    private static final String INPUT_QUEUE_NAME = "process.java.out";
    private static final String OUTPUT_QUEUE_NAME = "process.java.in";
    private static final String EXCHANGE = "test";
    private static final Gson GSON_PARSER = new Gson();

    private static volatile boolean running = true;

    public static void main(String[] args) throws URISyntaxException, NoSuchAlgorithmException, KeyManagementException, IOException, TimeoutException {
        Runtime.getRuntime().addShutdownHook(new Thread(() -> running=false));

        ConnectionFactory factory = new ConnectionFactory();
        String rabbitMQUrl = System.getenv("AMQP_URL");
        factory.setUri(rabbitMQUrl);
        try (Connection connection = factory.newConnection();
             Channel channel = connection.createChannel()) {
            channel.basicQos(1);
            channel.exchangeDeclare(EXCHANGE, BuiltinExchangeType.DIRECT, true, false, null);
            channel.queueDeclare(INPUT_QUEUE_NAME, true, false, false, null);
            channel.queueDeclare(OUTPUT_QUEUE_NAME, true, false, false, null);
            channel.queueBind(INPUT_QUEUE_NAME, EXCHANGE, INPUT_QUEUE_NAME);
            channel.queueBind(OUTPUT_QUEUE_NAME, EXCHANGE, OUTPUT_QUEUE_NAME);

            DeliverCallback deliverCallback = (consumerTag, delivery) -> {
                // Load JSON

                System.out.println("Received");
                try {
                    doWork(delivery.getBody(), channel);
                } catch (Exception e) {
                    System.out.println(e.getMessage());
                } finally {
                    channel.basicAck(delivery.getEnvelope().getDeliveryTag(), false);
                }
            };

            channel.basicConsume(INPUT_QUEUE_NAME, false, deliverCallback, consumerTag -> { });

            while (running) {
                Thread.onSpinWait();
            }
        }
     }

    private static void doWork(byte[] body, Channel channel) throws IOException {
        DataMessage dataMessage = loadJSON(body);

        channel.basicPublish("", OUTPUT_QUEUE_NAME,
                new AMQP.BasicProperties().builder().expiration("86400000")
                        .contentEncoding("binary").deliveryMode(2).build(),
                dumpJSON(dataMessage));
    }


    private static DataMessage loadJSON(byte[] gzippedEncodedInput) throws IOException {
        try (InputStream inputStream = new GZIPInputStream(new ByteArrayInputStream(gzippedEncodedInput))) {
            try (ByteArrayOutputStream outputStream = new ByteArrayOutputStream()) {
                inputStream.transferTo(outputStream);
                System.out.println(outputStream.toString(StandardCharsets.UTF_8));
                return GSON_PARSER.fromJson(outputStream.toString(StandardCharsets.UTF_8), DataMessage.class);
            }
        }
    }

    private static byte[] dumpJSON(DataMessage dataMessage) throws IOException {
        byte[] bytes = GSON_PARSER.toJson(dataMessage).getBytes();
        try (ByteArrayOutputStream bos = new ByteArrayOutputStream(bytes.length);
                GZIPOutputStream gos = new GZIPOutputStream(bos);
             ByteArrayInputStream bis = new ByteArrayInputStream(bytes)) {
            bis.transferTo(gos);
            return bos.toByteArray();

        }
    }
}
