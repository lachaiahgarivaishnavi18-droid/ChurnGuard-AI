
CREATE TABLE model_metrics (
	id SERIAL NOT NULL,
	version VARCHAR(64) NOT NULL,
	output JSON NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE,
	PRIMARY KEY (id),
	UNIQUE (version)
)

;


CREATE TABLE revoked_tokens (
	jti VARCHAR(64) NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE,
	PRIMARY KEY (jti)
)

;


CREATE TABLE users (
	id SERIAL NOT NULL,
	email VARCHAR(254) NOT NULL,
	password_hash VARCHAR(256) NOT NULL,
	role VARCHAR(20) NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (email)
)

;


CREATE TABLE bank_customers (
	id SERIAL NOT NULL,
	owner_id INTEGER NOT NULL,
	external_id VARCHAR(64) NOT NULL,
	name VARCHAR(120) NOT NULL,
	features JSON NOT NULL,
	historical_churn BOOLEAN,
	source VARCHAR(100) NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (owner_id, external_id),
	FOREIGN KEY(owner_id) REFERENCES users (id)
)

;


CREATE TABLE agent_executions (
	id VARCHAR(36) NOT NULL,
	customer_id INTEGER NOT NULL,
	owner_id INTEGER NOT NULL,
	status VARCHAR(20) NOT NULL,
	report JSON,
	created_at TIMESTAMP WITH TIME ZONE,
	PRIMARY KEY (id),
	FOREIGN KEY(customer_id) REFERENCES bank_customers (id) ON DELETE CASCADE,
	FOREIGN KEY(owner_id) REFERENCES users (id)
)

;


CREATE TABLE churn_predictions (
	id SERIAL NOT NULL,
	customer_id INTEGER NOT NULL,
	output JSON NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE,
	PRIMARY KEY (id),
	FOREIGN KEY(customer_id) REFERENCES bank_customers (id) ON DELETE CASCADE
)

;


CREATE TABLE customer_accounts (
	id SERIAL NOT NULL,
	customer_id INTEGER NOT NULL,
	snapshot JSON NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE,
	PRIMARY KEY (id),
	UNIQUE (customer_id),
	FOREIGN KEY(customer_id) REFERENCES bank_customers (id) ON DELETE CASCADE
)

;


CREATE TABLE customer_segments (
	id SERIAL NOT NULL,
	customer_id INTEGER NOT NULL,
	output JSON NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(customer_id) REFERENCES bank_customers (id) ON DELETE CASCADE
)

;


CREATE TABLE agent_execution_logs (
	id SERIAL NOT NULL,
	execution_id VARCHAR(36) NOT NULL,
	output JSON NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(execution_id) REFERENCES agent_executions (id)
)

;


CREATE TABLE churn_explanations (
	id SERIAL NOT NULL,
	prediction_id INTEGER NOT NULL,
	output JSON NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(prediction_id) REFERENCES churn_predictions (id) ON DELETE CASCADE
)

;


CREATE TABLE retention_recommendations (
	id SERIAL NOT NULL,
	customer_id INTEGER NOT NULL,
	execution_id VARCHAR(36) NOT NULL,
	output JSON NOT NULL,
	status VARCHAR(20) NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE,
	PRIMARY KEY (id),
	FOREIGN KEY(customer_id) REFERENCES bank_customers (id) ON DELETE CASCADE,
	FOREIGN KEY(execution_id) REFERENCES agent_executions (id)
)

;


CREATE TABLE analyst_feedback (
	id SERIAL NOT NULL,
	recommendation_id INTEGER NOT NULL,
	user_id INTEGER NOT NULL,
	decision VARCHAR(20) NOT NULL,
	note VARCHAR(2000) NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE,
	PRIMARY KEY (id),
	FOREIGN KEY(recommendation_id) REFERENCES retention_recommendations (id) ON DELETE CASCADE,
	FOREIGN KEY(user_id) REFERENCES users (id)
)

;

CREATE INDEX ix_bank_customers_owner_id ON bank_customers (owner_id);
CREATE INDEX ix_agent_executions_customer_id ON agent_executions (customer_id);
CREATE INDEX ix_agent_executions_owner_id ON agent_executions (owner_id);
CREATE INDEX ix_churn_predictions_customer_id ON churn_predictions (customer_id);
CREATE INDEX ix_customer_segments_customer_id ON customer_segments (customer_id);
CREATE INDEX ix_agent_execution_logs_execution_id ON agent_execution_logs (execution_id);
CREATE INDEX ix_retention_recommendations_customer_id ON retention_recommendations (customer_id);
