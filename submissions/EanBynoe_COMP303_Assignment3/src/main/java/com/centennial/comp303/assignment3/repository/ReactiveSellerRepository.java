package com.centennial.comp303.assignment3.repository;

import com.centennial.comp303.assignment3.model.Seller;
import org.springframework.data.mongodb.repository.ReactiveMongoRepository;
import reactor.core.publisher.Mono;

public interface ReactiveSellerRepository extends ReactiveMongoRepository<Seller, String> {
    Mono<Seller> findBySellerId(Long sellerId);
    Mono<Boolean> existsBySellerId(Long sellerId);
    Mono<Void> deleteBySellerId(Long sellerId);
}
