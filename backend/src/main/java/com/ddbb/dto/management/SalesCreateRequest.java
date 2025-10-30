package com.ddbb.dto.management;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class SalesCreateRequest {
    
    @NotNull(message = "빵 ID는 필수입니다")
    private Long breadId;
    
    @NotNull(message = "판매 수량은 필수입니다")
    @Min(value = 1, message = "판매 수량은 1 이상이어야 합니다")
    private Integer quantity;
}

