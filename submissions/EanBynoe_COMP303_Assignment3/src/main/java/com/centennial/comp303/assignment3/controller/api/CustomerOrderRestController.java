package com.centennial.comp303.assignment3.controller.api;

import com.centennial.comp303.assignment3.model.CustomerOrder;
import com.centennial.comp303.assignment3.service.CustomerOrderService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

@RestController
@RequestMapping("/api/orders")
public class CustomerOrderRestController {

    private final CustomerOrderService orderService;

    public CustomerOrderRestController(CustomerOrderService orderService) {
        this.orderService = orderService;
    }

    @GetMapping
    public Flux<CustomerOrder> getAllOrders() {
        return orderService.getAllOrders();
    }

    @GetMapping("/{orderId}")
    public Mono<CustomerOrder> getOrderById(@PathVariable Long orderId) {
        return orderService.getOrderById(orderId);
    }

    @GetMapping("/status/{status}")
    public Flux<CustomerOrder> getOrdersByStatus(@PathVariable String status) {
        return orderService.getOrdersByStatus(status);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public Mono<CustomerOrder> createOrder(@Valid @RequestBody CustomerOrder order) {
        return orderService.createOrder(order);
    }

    @PutMapping("/{orderId}/status")
    public Mono<CustomerOrder> updateStatus(@PathVariable Long orderId, @RequestParam String status) {
        return orderService.updateOrderStatus(orderId, status);
    }

    @PutMapping("/{orderId}/cancel")
    public Mono<CustomerOrder> cancelOrder(@PathVariable Long orderId) {
        return orderService.cancelOrderAndRestoreStock(orderId);
    }

    @DeleteMapping("/{orderId}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public Mono<Void> deleteOrder(@PathVariable Long orderId) {
        return orderService.deleteOrder(orderId);
    }
}
