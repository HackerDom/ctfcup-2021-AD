package ru.ctf.tcp;

import ru.ctf.db.TableAlleviator;
import ru.ctf.utils.BufferUtils;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.ServerSocketChannel;
import java.nio.channels.SocketChannel;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.logging.Level;
import java.util.logging.Logger;

public class TCPServer {
    private static final Logger LOG = Logger.getLogger(TCPServer.class.getName());
    private static final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
    private static final int BUFFER_SIZE = 1488;

    private final InetSocketAddress address = new InetSocketAddress("0.0.0.0", 8080);
    private final Map<SocketChannel, ByteBuffer> clientToBuffer = new ConcurrentHashMap<>();
    private final MessageHandler messageHandler = new MessageHandler();
    private final Map<SocketChannel, Long> connectionTime = new ConcurrentHashMap<>();
    private Selector selector;
    private ServerSocketChannel serverSocketChannel;


    public static void main(String[] args) {
        final TCPServer tcpServer = new TCPServer();
        try {
            configure(tcpServer);
        } catch (IOException e) {
            LOG.log(Level.SEVERE, e.getMessage());
        }
        Thread timeoutCheckerThread = new Thread(tcpServer.new TimeoutChecker());
        timeoutCheckerThread.start();
        tcpServer.startServer();
    }

    private static void configure(TCPServer server) throws IOException {
        server.configureServer();
        final TableAlleviator tableAlleviator = new TableAlleviator(16L);
        scheduler.scheduleAtFixedRate(tableAlleviator::alleviate, 17, 16, TimeUnit.MINUTES);
    }

    private void startServer() {
        LOG.info("Start server");
        while (true) {
            try {
                selector.select();
                Set<SelectionKey> selectedKeys = selector.selectedKeys();
                Iterator<SelectionKey> iter = selectedKeys.iterator();
                while (iter.hasNext()) {
                    SelectionKey selectionKey = iter.next();
                    if (selectionKey.isAcceptable()) {
                        acceptClient();
                    }

                    if (selectionKey.isReadable()) {
                        talk(selectionKey);
                    }
                }
            } catch (Exception ignored) {
            }
        }
    }

    private void talk(SelectionKey selectionKey) throws IOException {
        SocketChannel clientSocket = (SocketChannel) selectionKey.channel();
        ByteBuffer buffer = clientToBuffer.get(clientSocket);
        try {
            readSocket(clientSocket, buffer);
            byte[] byteMsg = BufferUtils.getNonZeroBytes(buffer);
            BufferUtils.fillBuffer(buffer,
                    messageHandler.handleMessage(BufferUtils.getStringFromBuffer(buffer), byteMsg));

            sendMessage(clientSocket, buffer);
        } catch (RuntimeException e) {
            sendBadMessage(clientSocket, buffer);
        }
    }

    private void acceptClient() throws IOException {
        SocketChannel client = serverSocketChannel.accept();
        if (client == null) {
            return;
        }
        client.configureBlocking(false);
        client.register(selector, SelectionKey.OP_READ);
        clientToBuffer.put(client, ByteBuffer.allocate(BUFFER_SIZE));
        connectionTime.put(client, System.currentTimeMillis());
        LOG.info("Connected to: " + client.getRemoteAddress());
    }

    private void configureServer() throws IOException {
        selector = Selector.open();
        serverSocketChannel = ServerSocketChannel.open();
        serverSocketChannel.bind(address);
        serverSocketChannel.configureBlocking(false);
        serverSocketChannel.register(selector, SelectionKey.OP_ACCEPT);
    }

    private void readSocket(SocketChannel clientSocket, ByteBuffer buffer) throws IOException {
        LOG.info("Work with: " + clientSocket.getRemoteAddress());
        BufferUtils.clearBuffer(buffer);
        clientSocket.read(buffer);
        buffer.clear();
        if (BufferUtils.findNonZeroByteIndex(buffer) > 200) {
            throw new RuntimeException();
        }
        LOG.info("message: " + BufferUtils.getStringFromBuffer(buffer) + " from " + clientSocket.getRemoteAddress());
    }

    private void sendMessage(SocketChannel clientSocket, ByteBuffer buffer) throws IOException {
        buffer.clear();
        if (BufferUtils.findNonZeroByteIndex(buffer) == 0) {
            clientToBuffer.remove(clientSocket);
            connectionTime.remove(clientSocket);
            clientSocket.close();
            LOG.info("Close connection " + clientSocket.getRemoteAddress());
            return;
        }
        clientSocket.write(buffer);
    }

    private void sendBadMessage(SocketChannel clientSocket, ByteBuffer buffer) throws IOException {
        BufferUtils.clearBuffer(buffer);
        buffer.put("some problems".getBytes());
        clientSocket.write(buffer);
        clientToBuffer.remove(clientSocket);
        connectionTime.remove(clientSocket);
        clientSocket.close();
        LOG.info("Close connection " + clientSocket.getRemoteAddress());
    }

    private void timeoutSanitizer(long timeout) throws IOException {
        long currentTime = System.currentTimeMillis();
        List<SocketChannel> clientsToDelete = new ArrayList<>();
        for (SocketChannel client : connectionTime.keySet()) {
            if (currentTime > connectionTime.get(client) + timeout) {
                clientToBuffer.remove(client);
                clientsToDelete.add(client);
                LOG.info("Close connection " + client.getRemoteAddress());
                client.close();
            }
        }
        for (SocketChannel client : clientsToDelete) {
            connectionTime.remove(client);
        }
    }

    private class TimeoutChecker implements Runnable {
        @Override
        public void run() {
            while (true) {
                try {
                    Thread.sleep(2000);
                    TCPServer.this.timeoutSanitizer(2000);
                } catch (InterruptedException | IOException e) {
                    throw new RuntimeException();
                }
            }
        }
    }
}
