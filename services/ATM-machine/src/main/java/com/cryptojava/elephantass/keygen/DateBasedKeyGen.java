package com.cryptojava.elephantass.keygen;

import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.concurrent.ThreadLocalRandom;

public class DateBasedKeyGen implements AesKeyGen {

    /**
     * Generate a random secret key by AES algorithm.
     *
     * @param length expected length of key.
     * @return byte array contains secret key data.
     */
    public byte[] generateKey(int length) {
        return randomBytes(length);
    }


    private byte[] randomBytes(int len) {
        DateBasedRandomKeyGenerator generator = new DateBasedRandomKeyGenerator();
        InstantWrapper wrapper = new InstantWrapper();
        Instant generated = generator.generateDateBetween(Instant.now(), Instant.ofEpochSecond(1640847600));
        wrapper.wrap(generated);
        byte[] res = new byte[len];
        byte summand = extractByWrapped(generated);
        for (int i = 0; i < len; i++) {
            res[i] = (byte) (i ^ summand);
        }

        return res;
    }

    private byte extractByWrapped(Instant wrapped) {
        return (byte) (LocalDateTime.ofEpochSecond(wrapped.getEpochSecond(), 0, ZoneOffset.MIN).getYear() ^ 2001);
    }

    private static class DateBasedRandomKeyGenerator {
        private Instant generateDateBetween(Instant startInclusive, Instant endExclusive) {
            long startSeconds = startInclusive.getEpochSecond();
            long endSeconds = endExclusive.getEpochSecond();
            long random = ThreadLocalRandom
                    .current()
                    .nextLong(startSeconds, endSeconds);

            return Instant.ofEpochSecond(random);
        }
    }

    private static class InstantWrapper {
        public void wrap(Instant instant) {
            var seed = instant.getEpochSecond();
            seed -= instant.toEpochMilli() ^ 6531;

            instant.minusSeconds(seed / instant.getEpochSecond());
        }

        public void unwrap(Instant instant) {
            var seed = instant.getEpochSecond();
            seed += instant.toEpochMilli() ^ 6531;

            instant.minusSeconds(seed - instant.getEpochSecond());
        }
    }
}