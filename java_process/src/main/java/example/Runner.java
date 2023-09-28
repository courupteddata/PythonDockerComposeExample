package example;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.networknt.schema.JsonSchema;
import com.networknt.schema.JsonSchemaFactory;
import com.networknt.schema.SpecVersion;
import com.networknt.schema.ValidationMessage;
import com.rabbitmq.client.*;


import java.io.*;
import java.net.URISyntaxException;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.security.KeyManagementException;
import java.security.NoSuchAlgorithmException;
import java.util.Set;
import java.util.concurrent.TimeoutException;
import java.util.zip.GZIPInputStream;
import java.util.zip.GZIPOutputStream;

public class Runner {
    private static final String INPUT_QUEUE_NAME = "process.java.out";
    private static final String OUTPUT_QUEUE_NAME = "process.java.in";
    private static final String EXCHANGE = "test";

    private static volatile boolean running = true;

    public static void main(String[] args) throws URISyntaxException, NoSuchAlgorithmException, KeyManagementException, IOException, TimeoutException {
        Runtime.getRuntime().addShutdownHook(new Thread(() -> running=false));

        InputStream resource = Runner.class.getClassLoader().getResourceAsStream("data_message.schema.json");
        JsonSchema jsonSchema =  JsonSchemaFactory.getInstance(SpecVersion.VersionFlag.V202012).getSchema(resource);
        jsonSchema.initializeValidators();
        ObjectMapper mapper = new ObjectMapper();



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
                    doWork(delivery.getBody(), channel, mapper, jsonSchema);
                } catch (Exception e) {
                    System.out.println(e.getMessage());
                } finally {
                    System.out.println("Done");
                    channel.basicAck(delivery.getEnvelope().getDeliveryTag(), false);
                }
            };

            channel.basicConsume(INPUT_QUEUE_NAME, false, deliverCallback, consumerTag -> { });

            while (running) {
                Thread.onSpinWait();
            }
        }
     }

    private static void doWork(byte[] body, Channel channel, ObjectMapper objectMapper, JsonSchema jsonSchema) throws IOException {
        JsonNode jsonNode = loadJSON(body, objectMapper);
        Set<ValidationMessage> errors = jsonSchema.validate(jsonNode);
        for (ValidationMessage validationMessage : errors) {
            System.out.println(validationMessage);
        }

        channel.basicPublish("", OUTPUT_QUEUE_NAME,
                new AMQP.BasicProperties().builder().expiration("86400000")
                        .contentEncoding("binary").deliveryMode(2).build(),
                dumpJSON(jsonNode, objectMapper));
    }


    private static JsonNode loadJSON(byte[] gzippedEncodedInput, ObjectMapper objectMapper) throws IOException {
        try (InputStream inputStream = new GZIPInputStream(new ByteArrayInputStream(gzippedEncodedInput))) {
            return objectMapper.readTree(inputStream);

        }
    }

    private static byte[] dumpJSON(JsonNode dataMessage, ObjectMapper objectMapper) throws IOException {

        try (ByteArrayOutputStream bos = new ByteArrayOutputStream();
                GZIPOutputStream gos = new GZIPOutputStream(bos);) {
            objectMapper.writer().writeValue(gos, dataMessage);
            return bos.toByteArray();
        }
    }

}
