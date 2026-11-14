package com.centennial.comp303.assignment3;

import com.centennial.comp303.assignment3.exception.InsufficientStockException;
import com.centennial.comp303.assignment3.model.CustomerOrder;
import com.centennial.comp303.assignment3.model.Product;
import com.centennial.comp303.assignment3.model.Seller;
import com.centennial.comp303.assignment3.repository.ReactiveCustomerOrderRepository;
import com.centennial.comp303.assignment3.repository.ReactiveProductRepository;
import com.centennial.comp303.assignment3.repository.ReactiveSellerRepository;
import com.centennial.comp303.assignment3.service.CustomerOrderService;
import com.centennial.comp303.assignment3.service.ProductService;
import com.centennial.comp303.assignment3.service.SellerService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import reactor.core.publisher.Mono;
import reactor.test.StepVerifier;

import java.time.LocalDateTime;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class MarketplaceServiceTests {

    @Mock
    private ReactiveSellerRepository sellerRepository;
    @Mock
    private ReactiveProductRepository productRepository;
    @Mock
    private ReactiveCustomerOrderRepository orderRepository;

    private SellerService sellerService;
    private ProductService productService;
    private CustomerOrderService orderService;

    @BeforeEach
    void setUp() {
        sellerService = new SellerService(sellerRepository);
        productService = new ProductService(productRepository, sellerRepository);
        orderService = new CustomerOrderService(orderRepository, productRepository);
    }

    @Test
    void createSeller_succeeds_whenUniqueId() {
        Seller seller = new Seller(101L, "TechHub Toronto", "sales@techhub.ca", "Small Business", "Toronto", 4.8);
        when(sellerRepository.existsBySellerId(101L)).thenReturn(Mono.just(false));
        when(sellerRepository.save(seller)).thenReturn(Mono.just(seller));

        StepVerifier.create(sellerService.createSeller(seller))
                .expectNextMatches(s -> s.getSellerId().equals(101L) && "TechHub Toronto".equals(s.getSellerName()))
                .verifyComplete();
    }

    @Test
    void createProduct_validatesSellerExists() {
        Product product = new Product(201L, "Mechanical Keyboard", "Electronics", 129.99, 10, true, 101L);
        when(sellerRepository.existsBySellerId(101L)).thenReturn(Mono.just(true));
        when(productRepository.existsByProductId(201L)).thenReturn(Mono.just(false));
        when(productRepository.save(product)).thenReturn(Mono.just(product));

        StepVerifier.create(productService.createProduct(product))
                .expectNextMatches(p -> p.getProductId().equals(201L) && p.getAvailability())
                .verifyComplete();
    }

    @Test
    void createOrder_decrementsStock_andCalculatesTotal() {
        Product product = new Product(201L, "Mechanical Keyboard", "Electronics", 100.0, 5, true, 101L);
        CustomerOrder order = new CustomerOrder(301L, "Ean Bynoe", "ean@example.com", 201L, 2, null, LocalDateTime.now());

        when(productRepository.findByProductId(201L)).thenReturn(Mono.just(product));
        when(productRepository.save(any(Product.class))).thenAnswer(inv -> Mono.just(inv.getArgument(0)));
        when(orderRepository.save(any(CustomerOrder.class))).thenAnswer(inv -> Mono.just(inv.getArgument(0)));

        StepVerifier.create(orderService.createOrder(order))
                .expectNextMatches(saved -> {
                    assertEquals(3, product.getStockQuantity());
                    assertEquals(200.0, saved.getTotalAmount());
                    assertEquals("Confirmed", saved.getOrderStatus());
                    return true;
                })
                .verifyComplete();
    }

    @Test
    void createOrder_failsWhenInsufficientStock() {
        Product product = new Product(201L, "Mechanical Keyboard", "Electronics", 100.0, 1, true, 101L);
        CustomerOrder order = new CustomerOrder(302L, "Ean Bynoe", "ean@example.com", 201L, 5, null, LocalDateTime.now());

        when(productRepository.findByProductId(201L)).thenReturn(Mono.just(product));

        StepVerifier.create(orderService.createOrder(order))
                .expectError(InsufficientStockException.class)
                .verify();
    }

    @Test
    void cancelOrder_restoresStock() {
        Product product = new Product(201L, "Mechanical Keyboard", "Electronics", 100.0, 3, true, 101L);
        CustomerOrder order = new CustomerOrder(301L, "Ean Bynoe", "ean@example.com", 201L, 2, "Confirmed", LocalDateTime.now());

        when(orderRepository.findByOrderId(301L)).thenReturn(Mono.just(order));
        when(productRepository.findByProductId(201L)).thenReturn(Mono.just(product));
        when(productRepository.save(any(Product.class))).thenAnswer(inv -> Mono.just(inv.getArgument(0)));
        when(orderRepository.save(any(CustomerOrder.class))).thenAnswer(inv -> Mono.just(inv.getArgument(0)));

        StepVerifier.create(orderService.cancelOrderAndRestoreStock(301L))
                .expectNextMatches(cancelled -> {
                    assertEquals("Cancelled", cancelled.getOrderStatus());
                    assertEquals(5, product.getStockQuantity());
                    return true;
                })
                .verifyComplete();
    }
}
