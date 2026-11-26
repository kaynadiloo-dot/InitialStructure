# Zeno Investments

Panel de inversiones en TypeScript que consulta y guarda datos en PostgreSQL a través de FastAPI.

## Ejecutar en Windows

Con PostgreSQL en ejecución, configurá `DATABASE_URL` en `backend/.env` con la base que querés usar. En PowerShell, desde `backend`:

```powershell
.\venv\Scripts\python.exe -m src.inversiones_app
.\venv\Scripts\python.exe -m uvicorn src.app:app --host 127.0.0.1 --port 8000 --reload
```

En otra terminal, desde `frontend` con Node.js 20.9 o superior:

```powershell
npm.cmd ci
npm.cmd run dev
```

Abrí [Zeno](http://localhost:3000). Next.js reenvía `/api/*` a FastAPI en `http://127.0.0.1:8000`. Si cambiás el puerto de FastAPI, copiá `.env.example` a `.env.local` y ajustá `API_URL`. La API se puede consultar en [Swagger](http://127.0.0.1:8000/docs).

El panel está pensado para una simulación local. Podés crear un inversor con su cuenta comitente o abrir un inversor existente por ID. Los precios se administran desde el catálogo. Las operaciones y los movimientos guardan sus cambios de saldo dentro de la misma transacción.

Las compras, ventas y conversiones MEP se pueden ejecutar de lunes a viernes desde las 11:00 hasta el cierre a las 17:00, hora de Buenos Aires. Para usar **Dólar MEP**, cargá y habilitá AL30 en ARS y AL30D en USD. El presupuesto de la orden incluye la comisión de compra. El historial registra las dos operaciones y el resultado de la conversión queda reflejado en ambos saldos.

La **Cartera** muestra valorización, rendimiento y composición por moneda. **Operaciones** permite filtrar por fecha, tipo de orden y ticker. Los resultados anuales suman las ventas que tienen una ganancia o pérdida realizada registrada. **Rankings** ordena los activos por unidades operadas en los últimos siete días y por cantidad de favoritos.

## Consultar los datos en pgAdmin

Abrí el Query Tool en la base indicada por `DATABASE_URL`. Por ejemplo:

```sql
SELECT i.id, i.nombre, c.numero_comitente, c.saldo_ars, c.saldo_usd
FROM public.inversores AS i
JOIN public.cuentas AS c ON c.inversor_id = i.id;

SELECT * FROM public.movimientos ORDER BY id DESC;
SELECT * FROM public.operaciones ORDER BY id DESC;
```
