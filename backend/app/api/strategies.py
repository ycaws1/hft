from fastapi import APIRouter

from app.models.domain import StrategyInfo, StrategyParamDef
from app.strategies.registry import strategy_registry

router = APIRouter(prefix="/api/strategies", tags=["strategies"])


@router.get("", response_model=list[StrategyInfo])
async def list_strategies():
    return [
        StrategyInfo(
            name=s.name,
            display_name=s.display_name,
            description=s.description,
            category=s.category,
        )
        for s in strategy_registry.all
    ]


@router.get("/{name}/params", response_model=list[StrategyParamDef])
async def get_strategy_params(name: str):
    strategy = strategy_registry.get(name)
    return strategy.parameters()
