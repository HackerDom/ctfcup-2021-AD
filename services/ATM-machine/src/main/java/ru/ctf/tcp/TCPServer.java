package ru.ctf.tcp;

import ru.ctf.db.TableAlleviator;
import ru.ctf.utils.ByteArrUtils;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.logging.Level;
import java.util.logging.Logger;

public class TCPServer {
    private static final Logger LOG = Logger.getLogger(TCPServer.class.getName());
    private static final ScheduledExecutorService dbScheduler = Executors.newScheduledThreadPool(1);
    private final ThreadPoolExecutor threadPoolExecutor = (ThreadPoolExecutor) Executors.newFixedThreadPool(128);
    private ServerSocket serverSocket;



    public static void main(String[] args) {
        final TCPServer tcpServer = new TCPServer();
        try {
            confServ(tcpServer);
            tcpServer.runServer();
        } catch (IOException e) {
            LOG.log(Level.SEVERE, e.getMessage());
        }
    }

    private static void confServ(TCPServer server) throws IOException {
        server.serverSocket = new ServerSocket(8080, 10, InetAddress.getByName("0.0.0.0"));
        final TableAlleviator tableAlleviator = new TableAlleviator(16L);
        dbScheduler.scheduleAtFixedRate(tableAlleviator::alleviate, 0, 16, TimeUnit.MINUTES);
    }

    private void runServer() throws IOException {
        LOG.info("Start server");
        while (true) {
            Socket client = serverSocket.accept();
            client.setSoTimeout(100);
            threadPoolExecutor.execute(new ClientHandler(client));
        }
    }

    private static class ClientHandler implements Runnable {
        private final Socket client;
        private InputStream clientInputStream;
        private OutputStream clientOutputStream;

        public ClientHandler(Socket client) {
            LOG.info("Client handler was created");
            this.client = client;
            try {
                this.clientInputStream = client.getInputStream();
                this.clientOutputStream = client.getOutputStream();
            } catch (IOException e) {
                LOG.warning("something went wrong");
                LOG.warning(e.getMessage());
            }
        }

        @Override
        public void run() {
            LOG.info("Start new talk");
            try {
                byte[] inBytes = readSocket();
                do {
                    byte[] answerBytes = getAnswer(inBytes);
                    sendMessage(answerBytes);
                    inBytes = readSocket();
                } while (inBytes != null && inBytes[0] != 0);
            } catch (RuntimeException e) {
                sendBadMessage();
            } finally {
                closeClient();
            }
        }

        private byte[] readSocket() {
            try {
                InputStream clientInputStream = client.getInputStream();
                byte[] inBytes = new byte[1000];
                clientInputStream.read(inBytes);
                return ByteArrUtils.getNonZeroBytes(inBytes);
            } catch (IOException e) {
                LOG.warning("can't read socket");
            }
            return null;
        }

        private byte[] getAnswer(byte[] msg) {
            MessageHandler messageHandler = new MessageHandler();
            return messageHandler.handleMessage(new String(msg).trim(), msg);
        }

        private void sendMessage(byte[] msg) {
            try {
                OutputStream clientOutputStream = client.getOutputStream();
                clientOutputStream.write(msg);
                clientOutputStream.flush();
            } catch (IOException e) {
                LOG.warning("can't write into socket");
            }
        }

        private void sendBadMessage() {
            try {
                client.getOutputStream().write("some problems".getBytes());
            } catch (IOException e) {
                LOG.warning("can't write bad msg");
            }
        }

        private void closeClient() {
            try {
                clientInputStream.close();
                clientOutputStream.close();
            } catch (IOException e) {
                LOG.warning("something does not work");
            };
        }
    }
}