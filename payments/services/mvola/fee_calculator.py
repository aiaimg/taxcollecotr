"""
MVola Fee Calculator Service

This module handles fee calculations for MVola transactions.
It calculates the 3% platform fee and extracts gateway fees from callback data.
"""

from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Dict


class MvolaFeeCalculator:
    """
    Calculate fees for MVola transactions.

    This service handles:
    - Calculating 3% platform fee on base tax amounts
    - Calculating total amounts including fees
    - Extracting gateway fees from MVola callback data
    """

    PLATFORM_FEE_PERCENTAGE = Decimal("3.00")  # 3%

    @staticmethod
    def calculate_total_amount(base_tax_amount: Decimal) -> Dict[str, Decimal]:
        """
        Calculate total amount including 3% platform fee.

        The platform fee is calculated as 3% of the base tax amount and rounded
        to the nearest Ariary using ROUND_HALF_UP rounding mode.

        Args:
            base_tax_amount: Base vehicle tax amount in Ariary

        Returns:
            dict: Dictionary containing:
                - base_amount: Original tax amount
                - platform_fee: Calculated 3% fee (rounded)
                - total_amount: Sum of base amount and platform fee

        Example:
            >>> result = MvolaFeeCalculator.calculate_total_amount(Decimal('100000'))
            >>> result['base_amount']
            Decimal('100000')
            >>> result['platform_fee']
            Decimal('3000')
            >>> result['total_amount']
            Decimal('103000')
        """
        # Calculate 3% fee
        platform_fee = (base_tax_amount * MvolaFeeCalculator.PLATFORM_FEE_PERCENTAGE / 100).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )

        # Calculate total amount
        total_amount = base_tax_amount + platform_fee

        return {"base_amount": base_tax_amount, "platform_fee": platform_fee, "total_amount": total_amount}

    @staticmethod
    def extract_gateway_fees(callback_data: Dict[str, Any]) -> Decimal:
        """
        Extract gateway fees from MVola callback data.

        MVola includes fee information in the callback payload under the 'fees' key.
        This method extracts the first fee amount if present, otherwise returns 0.

        Args:
            callback_data: Callback payload from MVola containing transaction details

        Returns:
            Decimal: Gateway fee amount in Ariary, or 0 if not present

        Example:
            >>> callback_data = {
            ...     'fees': [{'feeAmount': '500'}]
            ... }
            >>> MvolaFeeCalculator.extract_gateway_fees(callback_data)
            Decimal('500')

            >>> callback_data = {}
            >>> MvolaFeeCalculator.extract_gateway_fees(callback_data)
            Decimal('0')
        """
        fees = callback_data.get("fees", [])

        # Extract first fee amount if available
        if fees and len(fees) > 0:
            fee_amount = fees[0].get("feeAmount", 0)
            return Decimal(str(fee_amount))

        return Decimal("0")
