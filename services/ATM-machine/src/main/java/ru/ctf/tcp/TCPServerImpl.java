package ru.ctf.tcp;

import ru.ctf.utils.BufferUtils;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.SocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.ServerSocketChannel;
import java.nio.channels.SocketChannel;
import java.util.*;

public class TCPServerImpl implements TCPServer {
    private final static int BUFFER_SIZE = 1536;

    private final InetSocketAddress address = new InetSocketAddress("localhost", 8080);
    private final Map<SocketAddress, ByteBuffer> addressToBuffer = new HashMap<>();
    private final MessageHandler messageHandler = new MessageHandler();
    private Selector selector;
    private ServerSocketChannel serverSocketChannel;


    public static void main(String[] args) throws IOException {
        new TCPServerImpl().startServer();
    }

    private void startServer() throws IOException {
        configureServer();
        System.out.println("Start server");
        while (true) {
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
        }
    }

    private void talk(SelectionKey selectionKey) throws IOException {
        SocketChannel clientSocket = (SocketChannel) selectionKey.channel();
        ByteBuffer buffer = addressToBuffer.get(clientSocket.getRemoteAddress());

        readSocket(clientSocket, buffer);
        BufferUtils.fillBuffer(buffer, messageHandler.handleMessage(BufferUtils.getStringFromBuffer(buffer)));

        sendMessage(clientSocket, buffer);
    }

    private void acceptClient() throws IOException {
        SocketChannel client = serverSocketChannel.accept();
        if (client == null) {
            return;
        }
        client.configureBlocking(false);
        client.register(selector, SelectionKey.OP_READ);
        addressToBuffer.put(client.getRemoteAddress(), ByteBuffer.allocate(BUFFER_SIZE));
        System.out.println("Connected to: "  + client.getRemoteAddress());
    }

    private void configureServer() throws IOException {
        selector = Selector.open();
        serverSocketChannel = ServerSocketChannel.open();
        serverSocketChannel.bind(address);
        serverSocketChannel.configureBlocking(false);
        serverSocketChannel.register(selector, SelectionKey.OP_ACCEPT);
    }

    private void readSocket(SocketChannel clientSocket, ByteBuffer buffer) throws IOException {
        System.out.println("Work with: "  + clientSocket.getRemoteAddress());
        BufferUtils.clearBuffer(buffer);
        clientSocket.read(buffer);
        buffer.clear();
        System.out.println("message: " + BufferUtils.getStringFromBuffer(buffer) + " from " + clientSocket.getRemoteAddress());
    }

    private void sendMessage(SocketChannel clientSocket, ByteBuffer buffer) throws IOException {
        if (BufferUtils.findNonZeroByteIndex(buffer) == 0) {
            clientSocket.write(buffer);
            addressToBuffer.remove(clientSocket.getRemoteAddress());
            clientSocket.close();
            System.out.println("Close connection");
            return;
        }
        clientSocket.write(buffer);
    }
    
    
}
